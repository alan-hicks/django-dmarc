#----------------------------------------------------------------------
# Copyright (c) 2015-2018, Persistent Objects Ltd https://p-o.co.uk/
#
# License: BSD
#----------------------------------------------------------------------

from __future__ import unicode_literals

from django.apps import AppConfig

class DmarcConfig(AppConfig):
    name = 'dmarc'
    verbose_name = "DMARC feedback report manager"
