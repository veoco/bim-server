# Generated by Django 4.1 on 2022-08-12 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("speedtests", "0003_serverlist_server_ids"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="serverlist",
            name="servers",
        ),
    ]
