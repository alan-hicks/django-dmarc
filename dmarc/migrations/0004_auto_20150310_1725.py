# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dmarc', '0003_auto_20150307_1531'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='record',
            unique_together=set([]),
        ),
    ]
