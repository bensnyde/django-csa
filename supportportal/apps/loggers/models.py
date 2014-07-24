from django.conf import settings
from django.db import models
from datetime import datetime
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
import json
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out 
from django.utils.timesince import timesince

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class ActionLogger(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL)
    verb = models.CharField(max_length=64)
    obj = models.CharField(max_length=256, blank=False, null=False)
    parent = models.CharField(max_length=256)
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ('-timestamp', )

    def log(self, actor, verb, obj, parent=None):
        ActionLogger.objects.create(actor=actor, verb=verb, obj=obj, parent=parent)

    def dump_to_dict(self):
        action = "%s %s" % (self.verb, self.obj)
        if self.parent:
            action = "%s on %s" % (action, self.parent)

        return {
            'actor': self.actor.get_full_name(),
            'timestamp': self.timesince(),
            'action': action
        }

    def __unicode__(self):
        response = "%s %s %s" % (self.actor, self.verb, self.obj)
        if self.parent:
            response = response + " on %s" % self.parent

        return response

    def timesince(self, now=None):
        return timesince(self.timestamp, now)              

class RequestLogger(models.Model):
    timestamp = models.DateTimeField(default=datetime.now)
    uri = models.URLField(max_length=256)
    ip = models.IPAddressField()
    user_agent = models.CharField(max_length=256)
    request_method = models.CharField(max_length=16)
    get = models.CharField(max_length=256) 
    post = models.CharField(max_length=256)
    cookies = models.CharField(max_length=256)

    class Meta:
        abstract = True

    def __unicode__(self):
        return "%s request to %s @ %s" % (self.ip, self.uri, self.timestamp)

    def log(self, request):
        Request.objects.create(
            uri=request.build_absolute_uri(), 
            ip=get_client_ip(request), 
            user_agent=request.META['HTTP_USER_AGENT'], 
            request_method=request.META['REQUEST_METHOD'], 
            post=json.dumps(request.POST), 
            get=json.dumps(request.GET), 
            cookies=json.dumps(request.COOKIES)
        )        

    def timesince(self, now=None):
        return timesince(self.timestamp, now)        

class AuthenticationLogger(RequestLogger):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False)
    category = models.CharField(max_length=16, null=False, blank=False)

    def dump_to_dict(self):
        return {
            'user': self.user.get_full_name(),
            'category': self.category,
            'ip': self.ip,
            'user_agent': self.user_agent,
            'timestamp': self.timesince()
        }

    def log(self, request, user, category):
        AuthenticationLogger.objects.create(
            user=request.user,
            category=category,
            ip=get_client_ip(request), 
            user_agent=request.META['HTTP_USER_AGENT'], 
        )        

    def __unicode__(self):
        return "%s %s from %s @ %s" % (self.user, self.category, self.ip, self.timestamp)   

class ErrorLogger(RequestLogger):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False)
    message = models.CharField(max_length=512, null=False, blank=False)
    category = models.CharField(max_length=16, null=False, blank=False)

    def log(self, request, category, message):
        ErrorLogger.objects.create(
            user=request.user,
            message=message,
            category=category,
            uri=request.build_absolute_uri(), 
            ip=get_client_ip(request), 
            user_agent=request.META['HTTP_USER_AGENT'], 
            request_method=request.META['REQUEST_METHOD'], 
            post=json.dumps(request.POST), 
            get=json.dumps(request.GET), 
            cookies=json.dumps(request.COOKIES)
        )        


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    AuthenticationLogger().log(request, user, "Login")

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    AuthenticationLogger().log(request, user, "Logout")
