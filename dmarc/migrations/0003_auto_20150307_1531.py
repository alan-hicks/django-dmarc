# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dmarc', '0002_auto_20150303_1606'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='result',
            unique_together=set([]),
        ),
    ]
