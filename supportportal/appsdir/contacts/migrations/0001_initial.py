# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('companies', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(db_index=True, unique=True, max_length=64, verbose_name=b'Email Address', validators=[django.core.validators.EmailValidator()])),
                ('first_name', models.CharField(max_length=16, verbose_name=b'First Name')),
                ('last_name', models.CharField(max_length=16, verbose_name=b'Last Name')),
                ('title', models.CharField(max_length=16, null=True, blank=True)),
                ('personal_phone', models.CharField(max_length=16, null=True, verbose_name=b'Personal Phone Number', blank=True)),
                ('office_phone', models.CharField(max_length=16, null=True, verbose_name=b'Office Phone Number', blank=True)),
                ('fax', models.CharField(max_length=16, null=True, verbose_name=b'Fax Number', blank=True)),
                ('status', models.BooleanField(default=True)),
                ('notifications', models.BooleanField(default=True)),
                ('newsletter', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, to='companies.Company', null=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalContact',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('company_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('email', models.EmailField(db_index=True, max_length=64, verbose_name=b'Email Address', validators=[django.core.validators.EmailValidator()])),
                ('first_name', models.CharField(max_length=16, verbose_name=b'First Name')),
                ('last_name', models.CharField(max_length=16, verbose_name=b'Last Name')),
                ('title', models.CharField(max_length=16, null=True, blank=True)),
                ('personal_phone', models.CharField(max_length=16, null=True, verbose_name=b'Personal Phone Number', blank=True)),
                ('office_phone', models.CharField(max_length=16, null=True, verbose_name=b'Office Phone Number', blank=True)),
                ('fax', models.CharField(max_length=16, null=True, verbose_name=b'Fax Number', blank=True)),
                ('status', models.BooleanField(default=True)),
                ('notifications', models.BooleanField(default=True)),
                ('newsletter', models.BooleanField(default=False)),
                ('created', models.DateTimeField(editable=False, blank=True)),
                ('modified', models.DateTimeField(editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical contact',
            },
            bases=(models.Model,),
        ),
    ]
