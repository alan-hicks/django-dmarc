# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_ip', models.GenericIPAddressField()),
                ('recordcount', models.IntegerField()),
                ('policyevaluated_disposition', models.CharField(max_length=10)),
                ('policyevaluated_dkim', models.CharField(max_length=4)),
                ('policyevaluated_spf', models.CharField(max_length=4)),
                ('policyevaluated_reasontype', models.CharField(max_length=15, blank=True)),
                ('policyevaluated_reasoncomment', models.CharField(max_length=100, blank=True)),
                ('identifier_headerfrom', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('report_id', models.CharField(max_length=100)),
                ('date_begin', models.DateTimeField(db_index=True)),
                ('date_end', models.DateTimeField()),
                ('policy_domain', models.CharField(max_length=100)),
                ('policy_adkim', models.CharField(max_length=1, verbose_name=b'DKIM alignment mode')),
                ('policy_aspf', models.CharField(max_length=1, verbose_name=b'SPF alignment mode')),
                ('policy_p', models.CharField(max_length=10, verbose_name=b'Requested handling policy')),
                ('policy_sp', models.CharField(max_length=10, verbose_name=b'Requested handling policy for subdomains')),
                ('policy_pct', models.SmallIntegerField(verbose_name=b'Sampling rate')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reporter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('org_name', models.CharField(unique=True, max_length=100, verbose_name=b'Organisation')),
                ('email', models.EmailField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('record_type', models.CharField(max_length=4)),
                ('domain', models.CharField(max_length=100)),
                ('result', models.CharField(max_length=9)),
                ('record', models.ForeignKey(to='dmarc.Record', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='result',
            unique_together=set([('record', 'record_type', 'domain')]),
        ),
        migrations.AddField(
            model_name='report',
            name='reporter',
            field=models.ForeignKey(to='dmarc.Reporter', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='report',
            unique_together=set([('reporter', 'report_id', 'date_begin')]),
        ),
        migrations.AddField(
            model_name='record',
            name='report',
            field=models.ForeignKey(to='dmarc.Report', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='record',
            unique_together=set([('report', 'source_ip')]),
        ),
    ]
