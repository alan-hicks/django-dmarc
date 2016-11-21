#----------------------------------------------------------------------
# Copyright (c) 2015-2016, Persistent Objects Ltd http://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------

"""
DMARC models for managing Aggregate Reports
http://dmarc.org/resources/specification/
"""

from datetime import datetime
from django.db import models

class Reporter(models.Model):
    org_name = models.CharField('Organisation', unique=True, max_length=100)
    email = models.EmailField()

    def __unicode__(self):
        return self.org_name

class Report(models.Model):
    report_id = models.CharField(max_length=100)
    reporter = models.ForeignKey(Reporter)
    date_begin = models.DateTimeField(db_index=True)
    date_end = models.DateTimeField()
    policy_domain = models.CharField(max_length=100)
    policy_adkim = models.CharField('DKIM alignment mode', max_length=1)
    policy_aspf = models.CharField('SPF alignment mode', max_length=1)
    policy_p = models.CharField('Requested handling policy', max_length=10)
    policy_sp = models.CharField('Requested handling policy for subdomains', max_length=10)
    policy_pct = models.SmallIntegerField('Sampling rate')
    report_xml = models.TextField(blank=True)

    def __unicode__(self):
        return self.report_id

    class Meta:
        unique_together = (("reporter", "report_id", "date_begin"),)

class Record(models.Model):
    report = models.ForeignKey(Report, related_name='records')
    source_ip = models.CharField(max_length=39)
    recordcount = models.IntegerField()
    policyevaluated_disposition = models.CharField(max_length=10)
    policyevaluated_dkim = models.CharField(max_length=4)
    policyevaluated_spf = models.CharField(max_length=4)
    policyevaluated_reasontype = models.CharField(blank=True, max_length=75)
    policyevaluated_reasoncomment = models.CharField(blank=True, max_length=100)
    identifier_headerfrom = models.CharField(max_length=100)

    def __unicode__(self):
        return self.source_ip

class Result(models.Model):
    record = models.ForeignKey(Record, related_name='results')
    record_type = models.CharField(max_length=4)
    domain = models.CharField(max_length=100)
    result = models.CharField(max_length=9)

    def __unicode__(self):
        return "%s:%s-%s" % (str(self.id), self.record_type, self.domain,)
