# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dmarc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='report',
            field=models.ForeignKey(related_name='records', to='dmarc.Report'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='result',
            name='record',
            field=models.ForeignKey(related_name='results', to='dmarc.Record'),
            preserve_default=True,
        ),
    ]
