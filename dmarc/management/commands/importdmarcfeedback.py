#----------------------------------------------------------------------
# Copyright (c) 2015-2020, Persistent Objects Ltd https://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------
"""Import DMARC Feedback Reports
"""
import os, sys
import pytz
import logging
import tempfile

from datetime import datetime
from email import message_from_file, message_from_string
from email.generator import Generator
from email.utils import mktime_tz, parsedate_tz
from stat import S_ISREG
from io import StringIO
from time import timezone
from argparse import FileType

from django.db.utils import IntegrityError
from django.db import Error
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from dmarc.models import FBReporter, FBReport

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Command class for importing DMARC Feedback Reports
    Most errors are not raised to prevent email bounces
    """
    help = 'Imports a DMARC Feedback Report from an email'

    def add_arguments(self, parser):
        parser.add_argument('-e', '--email',
            type=FileType('r'),
            default=False,
            help='Import from email file, or - for stdin'
        )

    def handle(self, *args, **options):
        """
        Handle method to import a DMARC Feedback Report
        """

        logger.info("Importing DMARC Feedback Report")

        if not options['email']:
            msg = "Check usage, please supply a single DMARC report file or email"
            logger.error(msg)
            raise CommandError(msg)

        msg = 'Processing email'
        logger.debug(msg)

        try:
            email = options['email'].read()
            dmarcemail = message_from_string(email)
        except:
            msg = 'Unable to use email'
            logger.debug(msg)
            raise CommandError(msg)

        if dmarcemail.is_multipart():
            self.process_multipart(dmarcemail)
        else:
            self.process_822(dmarcemail)

    def process_multipart(self, dmarcemail):
        """Extract multipart report"""
        report = FBReport()
        dmarc_reporter = None
        try:
            dmarc_source = dmarcemail.get_payload()
            dmarc_reporter = dmarcemail.get('from')
            report.reporter = FBReporter.objects.get(email=dmarc_reporter)
            mimepart = dmarcemail.get_payload()
        except ObjectDoesNotExist:
            try:
                report.reporter = FBReporter.objects.create(
                    org_name = dmarc_reporter,
                    email = dmarc_reporter,
                )
            except:
                msg = 'Failed to find or create reporter {}'.format(dmarc_reporter)
                logger.error(msg)
                raise CommandError(msg)
        except:
            msg = 'Unable to get rfc822 report'
            logger.error(msg)
            tf = tempfile.mkstemp(prefix='dmarc-',suffix='.eml')
            tmpf = os.fdopen(tf[0],'w')
            tmpf.write(dmarcemail.get_payload())
            tmpf.close()
            msg = 'Saved as: {}'.format(tf[1])
            logger.error(msg)
            raise CommandError(msg)
        fp = StringIO()
        g = Generator(fp, maxheaderlen=0)
        g.flatten(dmarcemail)
        report.feedback_source = fp.getvalue()
        g = None
        fp = None

        # Get the human readable part
        try:
            mimepart = dmarcemail.get_payload(0)
            if mimepart.get_content_type() == 'text/plain':
                # get the human-readable part of the message
                report.description = mimepart
        except:
            msg = 'Unable to get human readable part'
            logger.warning(msg)

        # Get the feedback report
        try:
            mimepart = dmarcemail.get_payload(1)
            if mimepart.get_content_type() == 'message/feedback-report':
                fp = StringIO()
                g = Generator(fp, maxheaderlen=0)
                g.flatten(mimepart)
                report.feedback_report = fp.getvalue()
                g = None
                fp = None
            else:
                msg = 'Found {} instead of message/feedback-report'.format(mimepart.get_content_type())
                logger.error(msg)
        except:
            msg = 'Unable to get feedback-report part'
            logger.error(msg)

        if report.feedback_report:
            for line in report.feedback_report.splitlines():
                line = line.lstrip()
                (ls0, ls1, ls2) = line.partition(':')
                ls0 = ls0.strip()
                ls2 = ls2.strip()
                if ls1:
                    if not report.domain:
                        if ls0 == 'Reported-Domain':
                            report.domain = ls2
                    if not report.source_ip:
                        if ls0 == 'Source-IP':
                            report.source_ip = ls2
                    if not report.email_from:
                        if ls0 == 'Original-Mail-From':
                            report.email_from = ls2
                    if not report.date:
                        if ls0 == 'Arrival-Date':
                            try:
                                # get tuples
                                t = parsedate_tz(ls2)
                                # get timestamp
                                t = mktime_tz(t)
                                report.date = datetime.fromtimestamp(t)
                                tz_utc = pytz.timezone('UTC')
                                report.date = report.date.replace(tzinfo=tz_utc)
                            except:
                                msg = 'Unable to get date from: {}'.format(ls2)
                                logger.error(msg)
                                report.date = datetime.now()
                    if not report.dmarc_result:
                        if ls0 == 'Delivery-Result':
                            report.dmarc_result = ls2
                    if ls0 == 'Authentication-Results':
                        ar = ls2.split()
                        for r in ar:
                            (r0, r1, r2) = r.partition('=')
                            if r1:
                                if not report.dkim_alignment and r0 == 'dkim':
                                    report.dkim_alignment = r2.rstrip(';')
                                if not report.spf_alignment and r0 == 'spf':
                                    report.spf_alignment = r2.rstrip(';')

        # Get the rfc822 headers and any message
        fp = StringIO()
        g = Generator(fp, maxheaderlen=0)
        try:
            mimepart = dmarcemail.get_payload(2, False)
            mimepart_type = mimepart.get_content_type()
            g.flatten(mimepart)
            if mimepart_type == 'message/rfc822':
                report.email_source = fp.getvalue()
            elif mimepart_type == 'message/rfc822-headers':
                report.email_source = fp.getvalue()
            elif mimepart_type == 'text/rfc822':
                report.email_source = fp.getvalue()
            elif mimepart_type == 'text/rfc822-headers':
                report.email_source = fp.getvalue()
            else:
                msg = 'Found {} instead of rfc822'.format(mimepart_type)
                logger.debug(msg)
        except:
            msg = 'Unable to get rfc822 part'
            logger.warning(msg)
        g = None
        fp = None
        if report.email_source:
            for line in report.email_source.splitlines():
                line = line.lstrip()
                (ls0, ls1, ls2) = line.partition(':')
                ls0 = ls0.strip()
                ls2 = ls2.strip()
                if ls1:
                    if not report.email_subject:
                        if ls0 == 'Subject':
                            report.email_subject = ls2

        try:
            report.save()
        except:
            msg = 'Failed save from {}'.format(report.reporter)
            logger.error(msg)
            tf = tempfile.mkstemp(prefix='dmarc-',suffix='.eml')
            tmpf = os.fdopen(tf[0],'w')
            tmpf.write(dmarcemail.get_payload())
            tmpf.close()
            msg = 'Saved as: {}'.format(tf[1])
            logger.error(msg)

    def process_822(self, dmarcemail):
        """Extract report from rfc822 email, non standard"""
        report = FBReport()
        dmarc_reporter = None
        try:
            dmarc_reporter = dmarcemail.get('from')
            report.reporter = FBReporter.objects.get(email=dmarc_reporter)
        except ObjectDoesNotExist:
            try:
                report.reporter = FBReporter.objects.create(
                    org_name = dmarc_reporter,
                    email = dmarc_reporter,
                )
            except:
                msg = 'Failed to find or create reporter {}'.format(dmarc_reporter)
                logger.error(msg)
                raise CommandError(msg)
        except:
            msg = 'Unable to get feedback report'
            logger.warning(msg)
            tf = tempfile.mkstemp(prefix='dmarc-',suffix='.eml')
            tmpf = os.fdopen(tf[0],'w')
            tmpf.write(dmarcemail.get_payload())
            tmpf.close()
            msg = 'Saved as: {}'.format(tf[1])
            logger.error(msg)
            raise CommandError(msg)
        report.feedback_source = dmarcemail.get_payload()
        fp = StringIO()
        g = Generator(fp, maxheaderlen=0)
        g.flatten(dmarcemail)
        report.email_source = fp.getvalue()
        g = None
        fp = None

        for line in report.feedback_source.splitlines():
            line = line.lstrip()
            (ls0, ls1, ls2) = line.partition(':')
            ls0 = ls0.strip()
            ls2 = ls2.strip()
            if ls1:
                if not report.domain:
                    if ls0 == 'Sender Domain':
                        report.domain = ls2
                if not report.source_ip:
                    if ls0 == 'Sender IP Address':
                        report.source_ip = ls2
                if not report.date:
                    if ls0 == 'Received Date':
                        try:
                            # get tuples
                            t = parsedate_tz(ls2)
                            # get timestamp
                            t = mktime_tz(t)
                            report.date = datetime.fromtimestamp(t)
                            tz_utc = pytz.timezone('UTC')
                            report.date = report.date.replace(tzinfo=tz_utc)
                        except:
                            msg = 'Unable to get date from: {}'.format(ls2)
                            logger.error(msg)
                            report.date = datetime.now()
                if not report.spf_alignment:
                    if ls0 == 'SPF Alignment':
                        report.spf_alignment = ls2
                if not report.dkim_alignment:
                    if ls0 == 'DKIM Alignment':
                        report.dkim_alignment = ls2
                if not report.dmarc_result:
                    if ls0 == 'DMARC Results':
                        report.dmarc_result = ls2
                if not report.email_from:
                    if ls0 == 'From':
                        report.email_from = ls2
                if not report.email_subject:
                    if ls0 == 'Subject':
                        report.email_subject = ls2
        try:
            report.save()
        except:
            msg = 'Failed save from {}'.format(dmarc_reporter)
            logger.error(msg)
            tf = tempfile.mkstemp(prefix='dmarc-',suffix='.eml')
            tmpf = os.fdopen(tf[0],'w')
            tmpf.write(dmarcemail.get_payload())
            tmpf.close()
            msg = 'Saved as: {}'.format(tf[1])
            logger.error(msg)

