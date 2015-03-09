# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import appsdir.support.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalMacro',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('name', models.CharField(max_length=128)),
                ('body', models.TextField()),
                ('author_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('changed_by_id', models.IntegerField(db_index=True, null=True, editable=False, blank=True)),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical macro',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalPost',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('ticket_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('author_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('contents', models.TextField()),
                ('visible', models.BooleanField(default=True)),
                ('attachment', models.TextField(blank=True, max_length=100, null=True, validators=[appsdir.support.models.validate_file_extension])),
                ('rating', models.IntegerField(blank=True, null=True, choices=[(1, b'Needs improvement'), (2, b'Exemplary')])),
                ('changed_by_id', models.IntegerField(db_index=True, null=True, editable=False, blank=True)),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical post',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalQueue',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('title', models.CharField(max_length=128, db_index=True)),
                ('allow_email_submission', models.BooleanField(default=False)),
                ('email_address', models.EmailField(max_length=75, null=True, blank=True)),
                ('email_type', models.CharField(blank=True, max_length=5, null=True, choices=[(b'pop3', b'POP3'), (b'imap', b'IMAP4')])),
                ('email_host', models.CharField(max_length=128, null=True, blank=True)),
                ('email_port', models.IntegerField(null=True, blank=True)),
                ('email_ssl', models.BooleanField(default=False)),
                ('email_username', models.CharField(max_length=128, null=True, blank=True)),
                ('email_password', models.CharField(max_length=256, null=True, blank=True)),
                ('email_fetch_interval', models.IntegerField(default=5, null=True, blank=True)),
                ('email_last_checked', models.DateTimeField(null=True, editable=False, blank=True)),
                ('changed_by_id', models.IntegerField(db_index=True, null=True, editable=False, blank=True)),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical queue',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalTicket',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('tid', models.CharField(max_length=12, null=True, editable=False, db_index=True)),
                ('author_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('owner_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('priority', models.CharField(default=b'Normal', max_length=12, blank=True, choices=[(b'Low', b'Low'), (b'Normal', b'Normal'), (b'Urgent', b'Urgent')])),
                ('status', models.CharField(default=1, max_length=8, blank=True, choices=[(0, b'Closed'), (1, b'Open')])),
                ('flagged', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=256)),
                ('queue_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('due_date', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('staff_summary', models.TextField(null=True, blank=True)),
                ('satisfaction_rating', models.CharField(default=b'Unrated', max_length=12, blank=True, choices=[(b'Unrated', b'Unrated'), (b'Dissatisfied', b'Very Dissatisfied'), (b'Disappointed', b'Dissatisfied'), (b'Neutral', b'Neutral'), (b'Satisfied', b'Satisfied'), (b'Ecstatic', b'Very Satisfied')])),
                ('difficulty_rating', models.CharField(default=b'Unrated', max_length=12, blank=True, choices=[(b'Unrated', b'Unrated'), (b'Simple', b'Simple'), (b'Easy', b'Easy'), (b'Average', b'Medium'), (b'Difficult', b'Hard'), (b'Advanced', b'Advanced')])),
                ('changed_by_id', models.IntegerField(db_index=True, null=True, editable=False, blank=True)),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical ticket',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Macro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('body', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('changed_by', models.ForeignKey(related_name='support_macro_changed_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contents', models.TextField()),
                ('visible', models.BooleanField(default=True)),
                ('attachment', models.FileField(blank=True, null=True, upload_to=b'attachments/%Y/%m/%d', validators=[appsdir.support.models.validate_file_extension])),
                ('rating', models.IntegerField(blank=True, null=True, choices=[(1, b'Needs improvement'), (2, b'Exemplary')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('changed_by', models.ForeignKey(related_name='support_post_changed_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=128)),
                ('allow_email_submission', models.BooleanField(default=False)),
                ('email_address', models.EmailField(max_length=75, null=True, blank=True)),
                ('email_type', models.CharField(blank=True, max_length=5, null=True, choices=[(b'pop3', b'POP3'), (b'imap', b'IMAP4')])),
                ('email_host', models.CharField(max_length=128, null=True, blank=True)),
                ('email_port', models.IntegerField(null=True, blank=True)),
                ('email_ssl', models.BooleanField(default=False)),
                ('email_username', models.CharField(max_length=128, null=True, blank=True)),
                ('email_password', models.CharField(max_length=256, null=True, blank=True)),
                ('email_fetch_interval', models.IntegerField(default=5, null=True, blank=True)),
                ('email_last_checked', models.DateTimeField(null=True, editable=False, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('changed_by', models.ForeignKey(related_name='support_queue_changed_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tid', models.CharField(max_length=12, unique=True, null=True, editable=False, db_index=True)),
                ('priority', models.CharField(default=b'Normal', max_length=12, blank=True, choices=[(b'Low', b'Low'), (b'Normal', b'Normal'), (b'Urgent', b'Urgent')])),
                ('status', models.CharField(default=1, max_length=8, blank=True, choices=[(0, b'Closed'), (1, b'Open')])),
                ('flagged', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=256)),
                ('due_date', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('staff_summary', models.TextField(null=True, blank=True)),
                ('satisfaction_rating', models.CharField(default=b'Unrated', max_length=12, blank=True, choices=[(b'Unrated', b'Unrated'), (b'Dissatisfied', b'Very Dissatisfied'), (b'Disappointed', b'Dissatisfied'), (b'Neutral', b'Neutral'), (b'Satisfied', b'Satisfied'), (b'Ecstatic', b'Very Satisfied')])),
                ('difficulty_rating', models.CharField(default=b'Unrated', max_length=12, blank=True, choices=[(b'Unrated', b'Unrated'), (b'Simple', b'Simple'), (b'Easy', b'Easy'), (b'Average', b'Medium'), (b'Difficult', b'Hard'), (b'Advanced', b'Advanced')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(related_name='support_ticket_author', to=settings.AUTH_USER_MODEL)),
                ('changed_by', models.ForeignKey(related_name='support_ticket_changed_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('contacts', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
                ('owner', models.ForeignKey(related_name='support_ticket_owner', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('queue', models.ForeignKey(to='support.Queue')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='post',
            name='ticket',
            field=models.ForeignKey(to='support.Ticket'),
            preserve_default=True,
        ),
    ]
