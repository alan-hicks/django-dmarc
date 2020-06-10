#----------------------------------------------------------------------
# Copyright (c) 2015-2020, Persistent Objects Ltd https://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------
"""
DMARC views
https://dmarc.org/resources/specification/
"""
import csv
import datetime
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render

from dmarc.models import Report

class Echo(object):
    """An object that implements just the write method of the file-like
    interface for csv.writer.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def _sql_cursor(request_args):
    """Returns a cursor according to users request"""
    sql_where = []
    sql_orderby = []
    sql_params = []
    if 'dmarc_date_from' in request_args:
        val = request_args['dmarc_date_from']
        try:
            val = datetime.datetime.strptime(val, '%Y-%m-%d')
        except:
            val = datetime.date.today()
        sql_where.append('dmarc_report.date_begin >= %s')
        sql_params.append(val)
    if 'dmarc_date_to' in request_args:
        val = request_args['dmarc_date_to']
        try:
            val = datetime.datetime.strptime(val, '%Y-%m-%d')
        except:
            val = datetime.date.today()
        td = datetime.timedelta(days=1)
        val = val + td
        sql_where.append('dmarc_report.date_end < %s')
        sql_params.append(val)
    if 'dmarc_disposition' in request_args and request_args['dmarc_disposition']:
        val = request_args['dmarc_disposition']
        sql_where.append('dmarc_record.policyevaluated_disposition = %s')
        sql_params.append(val)
    if 'dmarc_onlyerror' in request_args:
        s = '('
        s = s + "dmarc_record.policyevaluated_dkim = 'fail'"
        s = s + " OR "
        s = s + "dmarc_record.policyevaluated_spf = 'fail'"
        s = s + ')'
        sql_where.append(s)
    if 'dmarc_filter' in request_args and request_args['dmarc_filter']:
        val = request_args['dmarc_filter'] + '%'
        s = '('
        s = s + "lower(dmarc_reporter.org_name) LIKE lower(%s)"
        s = s + " OR "
        s = s + "dmarc_record.source_ip LIKE %s"
        s = s + ')'
        sql_where.append(s)
        sql_params.append(val)
        sql_params.append(val)

    sql = """
SELECT
  dmarc_reporter.org_name,
  dmarc_reporter.email,
  dmarc_report.date_begin,
  dmarc_report.date_end,
  dmarc_report.policy_domain,
  dmarc_report.policy_adkim,
  dmarc_report.policy_aspf,
  dmarc_report.policy_p,
  dmarc_report.policy_sp,
  dmarc_report.policy_pct,
  dmarc_report.report_id,
  dmarc_record.source_ip,
  dmarc_record.recordcount,
  dmarc_record.policyevaluated_disposition,
  dmarc_record.policyevaluated_dkim,
  dmarc_record.policyevaluated_spf,
  dmarc_record.policyevaluated_reasontype,
  dmarc_record.policyevaluated_reasoncomment,
  dmarc_record.identifier_headerfrom,
  spf_dmarc_result.record_type AS spf_record_type,
  spf_dmarc_result.domain AS spf_domain,
  spf_dmarc_result.result AS spf_result,
  dkim_dmarc_result.record_type AS dkim_record_type,
  dkim_dmarc_result.domain AS dkim_domain,
  dkim_dmarc_result.result AS dkim_result
FROM dmarc_reporter
INNER JOIN dmarc_report
ON dmarc_report.reporter_id = dmarc_reporter.id
INNER JOIN  dmarc_record
ON dmarc_record.report_id = dmarc_report.id
LEFT OUTER JOIN dmarc_result AS spf_dmarc_result
ON spf_dmarc_result.record_id = dmarc_record.id
AND spf_dmarc_result.record_type = 'spf'
LEFT OUTER JOIN dmarc_result AS dkim_dmarc_result
ON dkim_dmarc_result.record_id = dmarc_record.id
AND dkim_dmarc_result.record_type = 'dkim'
    """

    if sql_where:
        sql = sql + " WHERE " + "\nAND ".join(sql_where)

    sql_orderby.append('LOWER(dmarc_reporter.org_name)')
    sql_orderby.append('dmarc_report.date_begin')
    sql_orderby.append('dmarc_record.source_ip')
    sql = sql + "\nORDER BY " + ", ".join(sql_orderby)

    cursor = connection.cursor()
    cursor.execute(sql, sql_params)

    return cursor

@staff_member_required
def dmarc_index(request):

    context = {
        "reports": 'TODO',
    }
    return render(request, 'dmarc/report.html', context)

@staff_member_required
def dmarc_report(request):
    report_list = Report.objects.select_related(
            'reporter',
        ).prefetch_related(
            'records__results'
        ).order_by('-date_begin', 'reporter__org_name').all()
    paginator = Paginator(report_list, 2)

    page = request.GET.get('page')
    try:
        reports = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reports = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reports = paginator.page(paginator.num_pages)

    context = {
        "reports": reports,
    }
    return render(request, 'dmarc/report.html', context)

@staff_member_required
def dmarc_csv(request):
    """Export dmarc data as a csv"""
    # Inspired by https://code.djangoproject.com/ticket/21179
    def stream():
        """Generator function to yield cursor rows."""
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        columns = True
        for row in cursor.fetchall():
            data = ''
            if columns:
                # Write the columns if this is the first row
                columns = [col[0] for col in cursor.description]
                data = writer.writerow(columns)
                columns = False
            data = data + writer.writerow(row)
            yield data

    dt = datetime.datetime.now()
    cd = 'attachment; filename="dmarc-{}.csv"'.format(dt.strftime('%Y-%m-%d-%H%M%S'))

    cursor = _sql_cursor(request.GET)

    response = StreamingHttpResponse(stream(), content_type="text/csv")
    response['Content-Disposition'] = cd

    return response

@staff_member_required
def dmarc_json(request):
    """Export dmarc data as json"""

    cursor = _sql_cursor(request.GET)

    data = response = JsonResponse(cursor.fetchall(), safe=False)
    return data

