from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class Announcement(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="%(app_label)s_%(class)s_author", editable=False, null=True)
    title = models.CharField(max_length=64)
    body = models.TextField()
    public = models.BooleanField(default=False, blank=True)
    status = models.BooleanField(default=True, blank=True)
    history = HistoricalRecords()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, related_name="%(app_label)s_%(class)s_changed_by")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created', )

    def __unicode__(self):
        return "%s" % self.title

    def get_absolute_url(self):
        return "/announcements/%i/" % self.id

    @property
    def _history_user(self):
        return self.changed_by