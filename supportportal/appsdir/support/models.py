import os, random, string
from datetime import datetime
from django.conf import settings
from django.db import models
from django.template import defaultfilters
from django.utils.timesince import timesince
from simple_history.models import HistoricalRecords
from appsdir.contacts.models import Contact

def validate_file_extension(filename):
    ext = os.path.splitext(filename.name)[1]
    valid_extensions = ['.pdf', '.jpg', '.png', '.txt']
    if ext not in valid_extensions:
        raise Exception('File extension not supported!')


class Queue(models.Model):
    EMAIL_TYPE_CHOICES = (
        ('pop3', 'POP3'),
        ('imap', 'IMAP4'),
    )

    title = models.CharField(max_length=128, unique=True)
    allow_email_submission = models.BooleanField(default=False, blank=True)
    email_address = models.EmailField(blank=True, null=True)
    email_type = models.CharField(max_length=5, blank=True, null=True, choices=EMAIL_TYPE_CHOICES)
    email_host = models.CharField(max_length=128, blank=True, null=True)
    email_port = models.IntegerField(blank=True, null=True)
    email_ssl = models.BooleanField(blank=True, default=False)
    email_username = models.CharField(max_length=128, blank=True, null=True)
    email_password = models.CharField(max_length=256, blank=True, null=True)
    email_fetch_interval = models.IntegerField(default=5, blank=True, null=True)
    email_last_checked = models.DateTimeField(blank=True, null=True, editable=False)
    history = HistoricalRecords()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, editable=False, related_name='%(app_label)s_%(class)s_changed_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.title

    def get_absolute_url(self):
        return '/api/support/queues/%i/' % self.id

    @property
    def _history_user(self):
        return self.changed_by


class Ticket(models.Model):
    STATUS_OPEN = 1
    STATUS_CLOSED = 0

    STATUS_CHOICES = (
        (STATUS_CLOSED, 'Closed'),
        (STATUS_OPEN, 'Open')
    )

    PRIORITY_1 = 'Low'
    PRIORITY_2 = 'Normal'
    PRIORITY_3 = 'Urgent'

    PRIORITY_CHOICES = (
        (PRIORITY_1, 'Low'),
        (PRIORITY_2, 'Normal'),
        (PRIORITY_3, 'Urgent'),
    )

    SATISFACTION_0 = 0
    SATISFACTION_1 = 1
    SATISFACTION_2 = 2
    SATISFACTION_3 = 3
    SATISFACTION_4 = 4
    SATISFACTION_5 = 5

    SATISFACTION_CHOICES = (
        (SATISFACTION_0, 'Unrated'),
        (SATISFACTION_1, 'Very Dissatisfied'),
        (SATISFACTION_2, 'Dissatisfied'),
        (SATISFACTION_3, 'Neutral'),
        (SATISFACTION_4, 'Satisfied'),
        (SATISFACTION_5, 'Very Satisfied')
    )

    DIFFICULTY_0 = 'Unrated'
    DIFFICULTY_1 = 'Simple'
    DIFFICULTY_2 = 'Easy'
    DIFFICULTY_3 = 'Average'
    DIFFICULTY_4 = 'Difficult'
    DIFFICULTY_5 = 'Advanced'

    DIFFICULTY_CHOICES = (
        (DIFFICULTY_0, 'Unrated'),
        (DIFFICULTY_1, 'Simple'),
        (DIFFICULTY_2, 'Easy'),
        (DIFFICULTY_3, 'Medium'),
        (DIFFICULTY_4, 'Hard'),
        (DIFFICULTY_5, 'Advanced')
    )

    tid = models.CharField(max_length=12, db_index=True, unique=True, editable=False, null=True)
    contacts = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(app_label)s_%(class)s_author')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='%(app_label)s_%(class)s_owner')
    priority = models.CharField(max_length=12, choices=PRIORITY_CHOICES, default=PRIORITY_2, blank=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=STATUS_OPEN, blank=True)
    flagged = models.BooleanField(default=False, blank=True)
    description = models.CharField(max_length=256)
    queue = models.ForeignKey(Queue)
    due_date = models.DateTimeField(default=datetime.now, blank=True)
    staff_summary = models.TextField(blank=True, null=True)
    satisfaction_rating = models.IntegerField(max_length=1, choices=SATISFACTION_CHOICES, blank=True, default=SATISFACTION_0)
    difficulty_rating = models.CharField(max_length=12, choices=DIFFICULTY_CHOICES, blank=True, default=DIFFICULTY_0)
    history = HistoricalRecords()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, editable=False, related_name='%(app_label)s_%(class)s_changed_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.description

    def get_absolute_url(self):
        return '/support/detail/%i/' % self.id

    def get_company(self):
        return self.author.company.id

    @property
    def _history_user(self):
        return self.changed_by

    def save(self, *args, **kwargs):
        if not self.tid:
            while True:
                tmp_tid = ''.join((random.choice(string.ascii_uppercase + string.digits) for _ in range(8)))
                if not Ticket.objects.filter(tid=tmp_tid):
                    self.tid = tmp_tid
                    break

        super(Ticket, self).save(*args, **kwargs)


class Post(models.Model):
    RATING_BAD = 1
    RATING_GOOD = 2

    RATING_CHOICES = (
        (RATING_BAD, 'Needs improvement'),
        (RATING_GOOD, 'Exemplary'),
    )

    ticket = models.ForeignKey(Ticket)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, editable=True, null=True)
    contents = models.TextField()
    visible = models.BooleanField(default=True, blank=True)
    attachment = models.FileField(upload_to='attachments/%Y/%m/%d', validators=[validate_file_extension], blank=True, null=True)
    rating = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)
    history = HistoricalRecords()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, editable=False, related_name='%(app_label)s_%(class)s_changed_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.contents

    def get_absolute_url(self):
        return '/support/detail/%i/#POST-%s' % (self.ticket.id, self.id)

    @property
    def _history_user(self):
        return self.changed_by


class Macro(models.Model):
    name = models.CharField(max_length=128)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    history = HistoricalRecords()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, related_name='%(app_label)s_%(class)s_changed_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % self.name

    def get_absolute_url(self):
        return '/api/support/macros/%i/' % self.id

    @property
    def _history_user(self):
        return self.changed_by