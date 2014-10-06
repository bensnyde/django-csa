from django.db import models

class Coupler(models.Model):
	name = models.CharField(max_length=64, blank=False, null=False)
	uri = models.SlugField(max_length=128, blank=False, null=False)

	def __unicode__(self):
		return self.name

class Service(models.Model):
	name = models.CharField(max_length=64, blank=False, null=False)
	coupler = models.ForeignKey(Coupler, blank=False, null=False)
	vars = models.CharField(max_length=256, blank=True, null=True)

	def __unicode__(self):
		return self.name

	def dump_to_dict(self):
		return {
			"pk": self.pk,
			"name": self.name,
			"coupler": self.coupler.name,
			"vars": self.vars
		}