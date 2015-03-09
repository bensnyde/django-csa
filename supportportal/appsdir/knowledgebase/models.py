from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


class Category(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True)
    title = models.SlugField(max_length=64, unique=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    history = HistoricalRecords()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, editable=False, related_name="%(app_label)s_%(class)s_changed_by")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % (self.title)

    def get_absolute_url(self):
        return "/knowledgebase/index/%i/" % self.id

    @property
    def _history_user(self):
        return self.changed_by


class Tag(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True)
    title = models.SlugField(max_length=64, unique=True)
    history = HistoricalRecords()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, editable=False, related_name="%(app_label)s_%(class)s_changed_by")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s' % (self.title)

    def get_absolute_url(self):
        return "/knowledgebase/index/0/%i/" % self.id

    @property
    def _history_user(self):
        return self.changed_by


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True)
    title = models.CharField(max_length=128)
    contents = models.TextField()
    views = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    history = HistoricalRecords()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, editable=False, related_name="%(app_label)s_%(class)s_changed_by")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True, blank=True)

    def __unicode__(self):
        return '%s' % (self.title)

    def get_absolute_url(self):
        return "/knowledgebase/detail/%i/" % self.id

    @property
    def _history_user(self):
        return self.changed_by