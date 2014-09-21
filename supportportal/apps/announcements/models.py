from django.conf import settings
from django.db import models
from datetime import datetime
from django.template import defaultfilters

class Announcement(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    timestamp = models.DateTimeField(default=datetime.now)
    title = models.CharField(max_length=256, blank=False, null=False)
    body = models.TextField(blank=False, null=False)
    public = models.BooleanField(default=False, blank=False)

    class Meta:
        ordering = ('-timestamp', )

    def dump_to_dict(self):
        return {
            'id': self.pk,
            'public': self.public,
            'author': self.author.get_full_name(),
            'timestamp': defaultfilters.date(self.timestamp, "SHORT_DATETIME_FORMAT"),
            'body': self.body,
            'title': self.title
        }

    def __unicode__(self):
        return "%s @ %s" % (self.author, self.timestamp)
