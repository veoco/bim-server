# Generated by Django 4.1 on 2022-08-17 06:11

from django.db import migrations


def add_ipv6(apps, schema_editor):
    import json
    with open("ipv6_data.json") as f:
        data = json.load(f)
        Server = apps.get_model("speedtests", "Server")
        for server in Server.objects.all():
            server.detail.update({"ipv6": data[str(server.pk)]})
            server.save()

class Migration(migrations.Migration):

    dependencies = [
        ("speedtests", "0004_remove_serverlist_servers"),
    ]

    operations = [
        migrations.RunPython(add_ipv6, migrations.RunPython.noop),
    ]
