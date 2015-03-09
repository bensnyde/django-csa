from __future__ import unicode_literals
from django.db import models, migrations
from appsdir.contacts.models import Contact
from django.contrib.auth.models import Group


def create_default_administrator_contact(apps, schema_editor):

    Group.objects.bulk_create([
        Group(name="Staff"),
        Group(name="Customer"),
        Group(name="Management")
    ])

    management_group = Group.objects.get(name="Management")

    contact = Contact.objects.create_user(email="root@example.com", first_name="Admin", last_name="Contact", password="password")
    contact.groups.add(management_group)
    contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        ('contenttypes', '__latest__'),
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_administrator_contact),
    ]