# Generated by Django 2.0 on 2018-01-15 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ServerInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(protocol='IPv4')),
                ('name', models.CharField(max_length=100)),
                ('uptime', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(choices=[(1, 'on_line'), (0, 'off_line')])),
            ],
        ),
    ]
