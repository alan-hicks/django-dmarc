#----------------------------------------------------------------------
# Copyright (c) 2015-2020, Persistent Objects Ltd https://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------

"""
DMARC models for managing Aggregate Reports
http://dmarc.org/resources/specification/
"""

from django.contrib import admin

from dmarc.models import Report

class ReportAdmin(admin.ModelAdmin):
    actions = []
    model = Report
    list_display = ['report_id', 'reporter', 'date_begin']
    list_filter = ['date_begin', 'reporter']
    readonly_fields = [
        'report_id', 'reporter',
        'date_begin', 'date_end', 'policy_domain',
        'policy_adkim', 'policy_aspf',
        'policy_p', 'policy_sp',
        'policy_pct',
        'report_xml'
    ]
    order = ['-id']

    def has_add_permission(self, request):
        return False

admin.site.register(Report, ReportAdmin)
