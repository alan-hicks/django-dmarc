#----------------------------------------------------------------------
# Copyright (c) 2015-2016, Persistent Objects Ltd http://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------
"""
DMARC views
http://dmarc.org/resources/specification/
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from dmarc.models import Report

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
