#----------------------------------------------------------------------
# Copyright (c) 2015-2016, Persistent Objects Ltd http://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------
"""
DMARC views
http://dmarc.org/resources/specification/
"""
import csv
import datetime

from StringIO import StringIO

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from django.http import StreamingHttpResponse
from django.shortcuts import render

from dmarc.models import Report

def _sql():
    return """
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
FROM public.dmarc_reporter
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
;
    """

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
        buffer_ = StringIO()
        writer = csv.writer(buffer_)
        columns = True
        for row in cursor.fetchall():
            if columns:
                # Write the columns if this is the first row
                columns = [col[0] for col in cursor.description]
                writer.writerow(columns)
                columns = False
            writer.writerow(row)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            yield data

    dt = datetime.datetime.now()
    cd = 'attachment; filename="dmarc-{}.csv"'.format(dt.strftime('%Y-%m-%d-%H%M%S'))

    sql = _sql()
    cursor = connection.cursor()
    cursor.execute(sql)

    response = StreamingHttpResponse(stream(), content_type="text/csv")
    response['Content-Disposition'] = cd

    return response
