from django.db import models
from datetime import datetime
from apps.services import Service

class Industry(models.Model):
	name = models.CharField(max_length=256, blank=False)

	def __unicode__(self):
		return u'%s' % (self.name)

class Company(models.Model):
	name = models.CharField(max_length=256, blank=False)
	description = models.TextField(blank=True)
	industry = models.ForeignKey(Industry, blank=True)
	created = models.DateTimeField(editable=False)
	modified = models.DateTimeField()
	website = models.CharField(max_length=256, blank=True)
	address1 = models.CharField(max_length=256, blank=True)
	address2 = models.CharField(max_length=256, blank=True)
	city = models.CharField(max_length=256, blank=True)
	state = models.CharField(max_length=256, blank=True)
	zip = models.CharField(max_length=256, blank=True)
	phone = models.CharField(max_length=100, blank=True)
	fax = models.CharField(max_length=100, blank=True)
	services = models.ManyToManyField(Service, blank=True)

	def __unicode__(self):
		return u'%s' % (self.name)

	def save(self, *args, **kwargs):
			''' On save, update timestamps '''
			if not self.id:
					self.created = datetime.today()
			self.modified = datetime.today()
			super(Company, self).save(*args, **kwargs)

def search(query):
	return Company.objects.filter(name__icontains=query)
