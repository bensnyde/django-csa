import random, string
from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


UID_LENGTH = 8

class Company(models.Model):
    name = models.CharField(max_length=32, unique=True, db_index=True)
    uid = models.CharField(max_length=UID_LENGTH, null=True, unique=True, editable=False)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address1 = models.CharField(max_length=64, blank=True, null=True)
    address2 = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=32, blank=True, null=True)
    state = models.CharField(max_length=16, blank=True, null=True)
    zip = models.CharField(max_length=16, blank=True, null=True)
    phone = models.CharField(max_length=16, blank=True, null=True)
    fax = models.CharField(max_length=16, blank=True, null=True)
    status = models.BooleanField(default=True, blank=True)
    history = HistoricalRecords()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="%(app_label)s_%(class)s_changed_by")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate UID on create
        if not self.uid:
            while True:
                hash = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(UID_LENGTH))
                if not Company.objects.filter(uid=hash):
                    self.uid = hash
                    break

        super(Company, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s' % (self.name)

    def get_absolute_url(self):
        return "/accounts/company/%i/" % self.id

    @property
    def _history_user(self):
        return self.changed_by