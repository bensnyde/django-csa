from django.db import models
from datetime import datetime
from apps.ip.models import NetworkAddress
from django.core.validators import RegexValidator, validate_ipv4_address

class Server(models.Model):
    TYPE_CHOICES = (
        ('KVM', 'Virtual - KVM'),
        ('VMWARE', 'Virtual - Vmware'),
        ('COLO', 'Physical - Colocated'),
        ('FARM', 'Physical - Farmed'),
    )

    name = models.CharField(max_length=256, validators=[RegexValidator(regex="^[a-zA-Z0-9 \',.-]*$", message='Only alphanumeric characters, spaces, commas, periods, hyphens and apostraphes are allowed.'),])
    ip = models.ForeignKey(NetworkAddress, blank=True, null=True)
    os = models.CharField(max_length=64, blank=True, null=True, validators=[RegexValidator(regex="^[a-zA-Z0-9 \',.-]*$", message='Only alphanumeric characters, spaces, commas, periods, hyphens and apostraphes are allowed.'),])
    username = models.CharField(max_length=64, blank=True, null=True, validators=[RegexValidator(regex="^[a-zA-Z0-9.-]*$", message='Only alphanumeric characters, periods, and hyphens are allowed.'),])
    password = models.CharField(max_length=256, blank=True, null=True)
    location = models.CharField(max_length=64, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 \\/(),.-]*$', message='Only alphanumeric characters, spaces, slashes, commas, periods, parentheses, and hyphens are allowed.'),])
    notes = models.TextField(blank=True, null=True)
    uplink = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=64)
    sid = models.CharField(max_length=128, blank=True, null=True)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
            ''' On save, update timestamps '''
            if not self.id:
                self.created = datetime.today()
            self.modified = datetime.today()
            super(Server, self).save(*args, **kwargs)    

    def dump_to_dict(self, full=False):
        response = {
            'id': self.pk,
            'name': self.name,
            'ip': str(self.ip),
            'os': self.os,
            'type': self.type,
        }

        if full is True:
            response.update({
                'username': self.username,
                'password': self.password, 
                'location': self.location,
                'uplink': self.uplink,
                'notes': self.notes
            })

        return response
