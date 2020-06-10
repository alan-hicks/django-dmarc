#----------------------------------------------------------------------
# Copyright (c) 2015-2020, Persistent Objects Ltd https://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------
"""Import DMARC Aggregate Reports
"""
import os, sys
import pytz
import xml.etree.ElementTree as ET
import gzip
import zipfile
import logging
import tempfile

from datetime import datetime
from email import message_from_file, message_from_string
from stat import S_ISREG
from io import StringIO
from time import timezone
from argparse import FileType

from django.db.utils import IntegrityError
from django.db import Error
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from dmarc.models import Reporter, Report, Record, Result

class Command(BaseCommand):
    """
    Command class for importing DMARC Aggregate Reports
    Most errors are not raised to prevent email bounces
    """
    help = 'Imports a DMARC Aggregate Report from either email or xml'

    def add_arguments(self, parser):
        parser.add_argument('-e', '--email',
            type=FileType('r'),
            default=False,
            help='Import from email file, or - for stdin'
        )
        parser.add_argument('-x', '--xml',
            type=FileType('r'),
            default=False,
            help='Import from xml file, or - for stdin'
        )

    def handle(self, *args, **options):
        """
        Handle method to import a DMARC Aggregate Reports
        Either pass in
        - the email message and the DMARC XML data will be extracted;
        - or the xml file.
        """

        logger = logging.getLogger(__name__)
        logger.info("Importing DMARC Aggregate Reports")

        dmarc_xml = ''

        if options['email']:
            email = options['email'].read()
            msg = 'Importing from email: {}'.format(email)
            dmarc_xml = self.get_xml_from_email(email)
        elif options['xml']:
            try:
                dmarc_xml = options['xml'].read()
            except:
                pass
            if not dmarc_xml:
                try:
                    # Test returns file name instead of file object
                    xml_file = open(options['xml'])
                    dmarc_xml = xml_file.read()
                except:
                    pass
            if not dmarc_xml:
                msg = "Unable to find DMARC file: {}".format(options['xml'])
                raise CommandError(msg)
            msg = 'Importing from xml: {}'.format(dmarc_xml)
            logger.debug(msg)
        else:
            msg = "Check usage, please supply a single DMARC report file or email"
            logger.error(msg)
            raise CommandError(msg)

        tz_utc = pytz.timezone('UTC')
        try:
            root = ET.fromstring(dmarc_xml)
        except:
            msg = "Processing xml failed: {}".format(dmarc_xml)
            logger.error(msg)
            return None

        # Report metadata
        report_metadata = root.findall('report_metadata')
        org_name = None
        email = None
        report_id = None
        report_begin = None
        report_end = None
        for node in report_metadata[0]:
            if node.tag == 'org_name':
                org_name = node.text
            if node.tag == 'email':
                email = node.text
            if node.tag == 'report_id':
                report_id = node.text
            if node.tag == 'date_range':
                report_begin = node.find('begin').text
                report_end = node.find('end').text

        if org_name is None:
            msg = "This DMARC report does not have an org_name"
            logger.error(msg)
        if report_id is None:
            msg = "This DMARC report for {} does not have a report_id".format(org_name)
            logger.error(msg)
        try:
            reporter = Reporter.objects.get(org_name=org_name)
        except ObjectDoesNotExist:
            try:
                reporter = Reporter.objects.create(org_name=org_name, email=email)
            except Error as e:
                msg = "Unable to create DMARC report for {}: {}".format(org_name, e)
                logger.error(msg)

        # Reporting policy
        policy_published = root.findall('policy_published')
        # Set defaults
        policy_domain = None
        policy_adkim = 'r'
        policy_aspf = 'r'
        policy_p = 'none'
        policy_sp = 'none'
        policy_pct = 0
        for node in policy_published[0]:
            if node.tag == 'domain':
                policy_domain = node.text
            if node.tag == 'adkim':
                policy_adkim = node.text
            if node.tag == 'aspf':
                policy_aspf = node.text
            if node.tag == 'p':
                policy_p = node.text
            if node.tag == 'sp':
                policy_sp = node.text
            if node.tag == 'pct':
                policy_pct = int(node.text)

        # Create the report
        report = Report()
        report.report_id = report_id
        report.reporter = reporter
        report_date_begin = datetime.fromtimestamp(float(report_begin)).replace(tzinfo=tz_utc)
        try:
            report_date_begin = datetime.fromtimestamp(float(report_begin)).replace(tzinfo=tz_utc)
            report_date_end = datetime.fromtimestamp(float(report_end)).replace(tzinfo=tz_utc)
        except:
            msg = "Unable to understand DMARC reporting dates"
            logger.error(msg)
        report.date_begin = report_date_begin
        report.date_end = report_date_end
        report.policy_domain = policy_domain
        report.policy_adkim = policy_adkim
        report.policy_aspf = policy_aspf
        report.policy_p = policy_p
        report.policy_sp = policy_sp
        report.policy_pct = policy_pct
        report.report_xml = dmarc_xml
        try:
            report.save()
        except IntegrityError as e:
            msg = "DMARC duplicate report record: {}".format(e)
            logger.error(msg)
            return None
        except Error as e:
            msg = "Unable to save the DMARC report header {}: {}".format(report_id, e)
            logger.error(msg)

        # Record
        for node in root.findall('record'):
            source_ip = None
            recordcount = 0
            policyevaluated_disposition = None
            policyevaluated_dkim = None
            policyevaluated_spf = None
            policyevaluated_reasontype = ''
            policyevaluated_reasoncomment = ''
            identifier_headerfrom = None
            row = node.find('row')
            source_ip = row.find('source_ip').text
            if row.find('count') is not None:
                recordcount = int(row.find('count').text)
            else:
                recordcount = 0
            policyevaluated = row.find('policy_evaluated')
            policyevaluated_disposition = policyevaluated.find('disposition').text
            policyevaluated_dkim = policyevaluated.find('dkim').text
            policyevaluated_spf = policyevaluated.find('spf').text
            if policyevaluated.find('reason') is not None:
                reason = policyevaluated.find('reason')
                if reason.find('type') is not None:
                    policyevaluated_reasontype = reason.find('type').text
                if reason.find('comment') is not None:
                    if reason.find('comment').text is not None:
                        policyevaluated_reasoncomment = reason.find('comment').text

            identifiers = node.find('identifiers')
            identifier_headerfrom = identifiers.find('header_from').text

            if len(source_ip) == 0:
                msg = "DMARC report record useless without a source ip"
                logger.error(msg)

            # Create the record
            record = Record()
            record.report = report
            record.source_ip = source_ip
            record.recordcount = recordcount
            record.policyevaluated_disposition = policyevaluated_disposition
            record.policyevaluated_dkim = policyevaluated_dkim
            record.policyevaluated_spf = policyevaluated_spf
            record.policyevaluated_reasontype = policyevaluated_reasontype
            record.policyevaluated_reasoncomment = policyevaluated_reasoncomment
            record.identifier_headerfrom = identifier_headerfrom
            try:
                record.save()
            except IntegrityError as e:
                msg = "DMARC duplicate record: {}".format(e)
                logger.error(msg)
            except Error as e:
                msg = "Unable to save the DMARC report record: {}".format(e)
                logger.error(msg)

            auth_results = node.find('auth_results')
            for resulttype in auth_results:
                result_domain = resulttype.find('domain').text
                if result_domain is None:
                    # Allow for blank domains
                    result_domain = ''
                result_result = resulttype.find('result').text

                # Create the record
                result = Result()
                result.record = record
                result.record_type = resulttype.tag
                result.domain = result_domain
                result.result = result_result
                try:
                    result.save()
                except Error as e:
                    msg = "Unable to save the DMARC report result {} for {}: {}".format(resulttype.tag, result_domain, e.message)
                    logger.error(msg)

    def get_xml_from_email(self, email):
        """Get xml from an email
        """
        dmarc_xml = ''
        logger = logging.getLogger(__name__)

        msg = 'Processing email'
        logger.debug(msg)
        try:
            dmarcemail = message_from_string(email)
        except:
            msg = 'Unable to use email'
            logger.debug(msg)
            return ''

        for mimepart in dmarcemail.walk():
            msg = 'Processing content type: {}'.format(mimepart.get_content_type())
            logger.debug(msg)
            if mimepart.get_content_type() == 'application/x-zip-compressed' \
                or mimepart.get_content_type() == 'application/x-zip' \
                or mimepart.get_content_type() == 'application/zip' \
                or mimepart.get_content_type() == 'application/gzip' \
                or mimepart.get_content_type() == 'application/octet-stream':
                dmarc_zip = StringIO()
                dmarc_zip.write(mimepart.get_payload(decode=True))
                dmarc_zip.seek(0)
                if zipfile.is_zipfile(dmarc_zip):
                    msg = "DMARC is zipfile"
                    logger.debug(msg)
                    try:
                        ZipFile = zipfile.ZipFile(dmarc_zip, 'r')
                        files = ZipFile.infolist()
                        # The DMARC report should only contain a single xml file
                        for f in files:
                            dmarc_xml = ZipFile.read(f)
                        ZipFile.close()
                    except (zipfile.BadZipfile):
                        msg = 'Unable to unzip mimepart'
                        logger.error(msg)
                        tf = tempfile.mkstemp(prefix='dmarc-',suffix='.zip')
                        dmarc_zip.seek(0)
                        tmpf = os.fdopen(tf[0],'w')
                        tmpf.write(dmarc_zip.getvalue())
                        tmpf.close()
                        msg = 'Saved in: {}'.format(tf[1])
                        logger.debug(msg)
                        raise CommandError(msg)
                else:
                    msg = "DMARC trying gzip"
                    logger.debug(msg)
                    # Reset zip file
                    dmarc_zip.seek(0)
                    try:
                        ZipFile = gzip.GzipFile(None, 'rb', 0, dmarc_zip)
                        dmarc_xml = ZipFile.read()
                        ZipFile = None
                        msg = "DMARC successfully extracted xml from gzip"
                        logger.debug(msg)
                    except:
                        msg = 'Unable to gunzip mimepart'
                        logger.error(msg)
                        tf = tempfile.mkstemp(prefix='dmarc-',suffix='.gz')
                        dmarc_zip.seek(0)
                        tmpf = os.fdopen(tf[0],'w')
                        tmpf.write(dmarc_zip.getvalue())
                        tmpf.close()
                        msg = 'Saved in: {}'.format(tf[1])
                        logger.debug(msg)
                        raise CommandError(msg)
            else:
                try:
                    myname = mimepart.get_filename()
                except:
                    myname = 'Not provided'
                msg = "DMARC Report is not in mimepart: {}".format(myname)
                logger.debug(msg)
        return dmarc_xml

