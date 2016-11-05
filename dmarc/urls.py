#----------------------------------------------------------------------
# Copyright (c) 2015-2016, Persistent Objects Ltd http://p-o.co.uk/
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
    url("^report/$", views.dmarc_report),
    url("^csv/$", views.dmarc_csv, name='dmarc_csv'),
]
