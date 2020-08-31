# Generated by Django 3.1 on 2020-08-19 06:07

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('study_helper_app', '0014_auto_20200818_0823'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stage',
            name='interval_month',
        ),
        migrations.AlterField(
            model_name='cart',
            name='repeat_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 8, 19, 6, 6, 59, 853653, tzinfo=utc), verbose_name='Дата Повторения'),
        ),
    ]
