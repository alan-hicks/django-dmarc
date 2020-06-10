# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dmarc', '0004_auto_20150310_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='report_xml',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
