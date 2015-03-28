#----------------------------------------------------------------------
# Copyright (c) 2015, Persistent Objects Ltd http://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------
"""Import DMARC Aggregate Reports
"""
from __future__ import unicode_literals

import os, sys
import pytz
import xml.etree.ElementTree as ET
import zipfile
import logging

from datetime import datetime
from email import message_from_file
from stat import S_ISREG
from cStringIO import StringIO
from time import timezone

from django.db import Error
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from dmarc.models import Reporter, Report, Record, Result

class Command(BaseCommand):
    """
    Command class for importing DMARC Aggregate Reports
    """
    args = '<dmarc_report>'
    help = 'Imports a DMARC Aggregate Reports'

    def handle(self, *args, **options):
        """
        Handle method to import a DMARC Aggregate Reports
        Either pass in
        - the email message and the DMARC XML data will be extracted;
        - the zip file and the xmlf iel will be extracted;
        - or the xml file.
        """

        logger = logging.getLogger(__name__)
        logger.info("Importing DMARC Aggregate Reports")
        supress_errors = False

        dmarc_iszipfile = False
        dmarc_xml = ''
        dmarc_file = ''

        if len(args) == 1:
            if args[0] == '-':
                # The report is an email passed via a pipe
                # Ignore errors to prevent email bounces
                supress_errors = True
                email_msg = StringIO()
                for line in sys.stdin:
                    email_msg.write(line)
                email_msg.seek(0)
                if email_msg:
                    dmarcemail = message_from_file(email_msg)
                    for mimepart in dmarcemail.walk():
                        if mimepart.get_content_type() == 'application/x-zip-compressed' \
                            or mimepart.get_content_type() == 'application/x-zip' \
                            or mimepart.get_content_type() == 'application/zip':
                            dmarc_zip = StringIO()
                            dmarc_zip.write(mimepart.get_payload(decode=True))
                            dmarc_zip.seek(0)
                            ZipFile = zipfile.ZipFile(dmarc_zip, 'r')
                            files = ZipFile.infolist()
                            # The DMARC report should only contain a single xml file
                            for f in files:
                                dmarc_xml = ZipFile.read(f)
                            ZipFile.close()
                            dmarc_iszipfile = True
            else:
                # We were passed a file name
                dmarc_file = args[0]
                if os.path.exists(dmarc_file):
                    msg = "Found %s" % dmarc_file
                    logger.debug(msg)
                else:
                    msg = "Unable to find DMARC file: %s" % dmarc_file
                    logger.error(msg)
                    raise CommandError(msg)

                mode = os.stat(dmarc_file).st_mode
                if not S_ISREG(mode):
                    msg = "Unable to read DMARC file: %s" % dmarc_file
                    logger.error(msg)
                    raise CommandError(msg)
                msg = "Importing DMARC: %s" % dmarc_file
                logger.debug(msg)

                if zipfile.is_zipfile(dmarc_file):
                    dmarc_iszipfile = True
                    ZipFile = zipfile.ZipFile(dmarc_file, 'r')
                    files = ZipFile.infolist()
                    # The DMARC report should only contain a single xml file
                    for f in files:
                        dmarc_xml = ZipFile.read(f)
                    ZipFile.close()
        else:
            msg = "Check usage, please supply a single DMARC report file or - for email on stdin"
            logger.error(msg)
            raise CommandError(msg)

        tz_utc = pytz.timezone('UTC')

        # Open and parse the DMARC report
        # Exctract the xml report and hold in memory for storage
        # Reports are fairly small so should not have much impact.
        report_xml = ''
        if dmarc_iszipfile:
            report_xml = dmarc_xml
            root = ET.fromstring(dmarc_xml)
        else:
            tree = ET.parse(dmarc_file)
            report_xml_stringio = StringIO()
            tree.write(report_xml_stringio, encoding="utf-8", xml_declaration=True)
            report_xml_stringio.seek(0)
            report_xml = report_xml_stringio.readlines()
            root = tree.getroot()

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
            if not supress_errors:
                raise CommandError(msg)
        if report_id is None:
            msg = "This DMARC report for %s does not have a report_id" % org_name
            logger.error(msg)
            if not supress_errors:
                raise CommandError(msg)
        try:
            reporter = Reporter.objects.get(org_name=org_name)
        except ObjectDoesNotExist:
            try:
                reporter = Reporter.objects.create(org_name=org_name, email=email)
            except Error as e:
                msg = "Unable to create DMARC report for %s: $s" % (org_name, e)
                logger.error(msg)
                if not supress_errors:
                    raise CommandError(msg)

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
            if not supress_errors:
                raise CommandError(msg)
        report.date_begin = report_date_begin
        report.date_end = report_date_end
        report.policy_domain = policy_domain
        report.policy_adkim = policy_adkim
        report.policy_aspf = policy_aspf
        report.policy_p = policy_p
        report.policy_sp = policy_sp
        report.policy_pct = policy_pct
        report.report_xml = report_xml
        try:
            report.save()
        except Error as e:
            msg = "Unable to save the DMARC report header %s: %s" % (report_id, e)
            logger.error(msg)
            if not supress_errors:
                raise CommandError(msg)

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
                if not supress_errors:
                    raise CommandError(msg)

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
            record.save()
            try:
                record.save()
            except Error as e:
                msg = "Unable to save the DMARC report record: %s" % e
                logger.error(msg)
                if not supress_errors:
                    raise CommandError(msg)

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
                    msg = "Unable to save the DMARC report result %s for %s: %s" % (resulttype.tag, result_domain, e.message)
                    logger.error(msg)
                    if not supress_errors:
                        raise CommandError(msg)
