# Generated by Django 2.0 on 2018-01-24 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crontab_formal', '0004_resultlog_subversion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resultlog',
            name='event_type',
            field=models.IntegerField(choices=[(0, '执行调度'), (1, '开始执行'), (2, '正常结束'), (3, '异常终止'), (4, '质控正常'), (5, '质控异常')]),
        ),
    ]
