#----------------------------------------------------------------------
# Copyright (c) 2015, Persistent Objects Ltd http://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------
"""
DMARC urls
http://dmarc.org/resources/specification/
"""
from django.conf.urls import patterns, url

urlpatterns = []

urlpatterns += patterns("dmarc.views",
    url("^dmarc/report/$", "dmarc_report", name="dmarc_report"),
)
