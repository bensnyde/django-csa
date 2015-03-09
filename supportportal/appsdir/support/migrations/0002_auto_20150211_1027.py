from __future__ import unicode_literals
from django.db import models, migrations


def create_default_ticket_queues(apps, schema_editor):
    Queue = apps.get_model('support', 'Queue')
    Queue.objects.bulk_create([
        Queue(title="Technical"),
        Queue(title="Billing"),
        Queue(title="Sales"),
        Queue(title="Management"),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_ticket_queues),
    ]