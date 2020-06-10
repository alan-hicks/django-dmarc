# -*- coding: utf-8 -*-

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dmarc', '0005_report_report_xml'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='policyevaluated_reasontype',
            field=models.CharField(max_length=75, blank=True),
        ),
        migrations.AlterField(
            model_name='reporter',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
