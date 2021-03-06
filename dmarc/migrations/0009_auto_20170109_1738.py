# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-09 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dmarc', '0008_auto_20170108_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='fbreport',
            name='feedback_report',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='fbreport',
            name='feedback_source',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fbreport',
            name='description',
            field=models.TextField(blank=True, verbose_name=b'human readable feedback'),
        ),
        migrations.AlterField(
            model_name='fbreport',
            name='email_source',
            field=models.TextField(blank=True, verbose_name=b'source email including rfc822 headers'),
        ),
    ]
