from django.conf import settings
from django.db import models
from datetime import datetime
from django.template import defaultfilters

class News(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    timestamp = models.DateTimeField(default=datetime.now)
    title = models.CharField(max_length=256)
    body = models.TextField()

    class Meta:
        ordering = ('-timestamp', )

    def dump_to_dict(self):
        return {
            'author': self.author.get_full_name(),
            'timestamp': defaultfilters.date(self.timestamp, "SHORT_DATETIME_FORMAT"),
            'body': self.body,
            'title': self.title 
        }

    def __unicode__(self):
        return "%s @ %s" % (self.author, self.timestamp)            