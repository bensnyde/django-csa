from django.conf import settings
from django.db import models
from datetime import datetime
from django.utils.timesince import timesince


class AuthenticationLogger(models.Model):
    ACTION_CHOICES = (
        ("LOGOUT", "Logout"),
        ("LOGIN", "Login"),
    )

    created = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=128)
    request_method = models.CharField(max_length=8)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False)
    action = models.CharField(choices=ACTION_CHOICES, max_length=8, null=False, blank=False)

    def __unicode__(self):
        return "%s %s from %s @ %s" % (self.user, self.action, self.ip, self.created)

    def timesince(self, now=None):
        return timesince(self.created, now)