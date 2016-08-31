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

urlpatterns = [
    url("^report/$", views.dmarc_report),
]
