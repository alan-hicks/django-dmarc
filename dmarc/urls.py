#----------------------------------------------------------------------
# Copyright (c) 2015-2020, Persistent Objects Ltd https://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------
"""
DMARC urls
http://dmarc.org/resources/specification/
"""
from django.conf.urls import url
from dmarc import views

app_name = 'dmarc'
urlpatterns = [
    url("^report/$", views.dmarc_report, name='dmarc_report'),
    url("^report/csv/$", views.dmarc_csv, name='dmarc_csv'),
    url("^report/json/$", views.dmarc_json, name='dmarc_json'),
]
