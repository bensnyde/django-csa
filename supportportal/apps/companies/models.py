from django.db import models
from datetime import datetime
from apps.services.models import Service
from django.core.validators import RegexValidator
from django.utils.dateformat import DateFormat


class Company(models.Model):
	name = models.CharField(max_length=255, unique=True, db_index=True, validators=[RegexValidator(regex="^[a-zA-Z0-9 \',.-]*$", message='Only alphanumeric characters, spaces, commas, periods, hyphens and apostraphes are allowed.'),])
	description = models.TextField(blank=True, null=True)
	created = models.DateTimeField(editable=False)
	modified = models.DateTimeField()
	website = models.URLField(blank=True, null=True)
	address1 = models.CharField(max_length=256, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 \'#,.-]*$', message='Only alphanumeric characters, spaces, pounds, commas, periods, hyphens and apostraphes are allowed.'),])
	address2 = models.CharField(max_length=256, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 \'#,.-]*$', message='Only alphanumeric characters, spaces, pounds, commas, periods, hyphens and apostraphes are allowed.'),])
	city = models.CharField(max_length=128, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 \',.-]*$', message='Only alphanumeric characters, spaces, commas, periods, hyphens and apostraphes are allowed.'),])
	state = models.CharField(max_length=128, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 \',.-]*$', message='Only alphanumeric characters, spaces, commas, periods, hyphens and apostraphes are allowed.'),])
	zip = models.CharField(max_length=128, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 \',.-]*$', message='Only alphanumeric characters, spaces, commas, periods, hyphens and apostraphes are allowed.'),])
	phone = models.CharField(max_length=64, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 ()-]*$', message='Only alphanumeric characters, spaces, paraentheses, and hyphens are allowed.'),])
	fax = models.CharField(max_length=64, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 ()-]*$', message='Only alphanumeric characters, spaces, paraentheses, and hyphens are allowed.'),])
	services = models.ManyToManyField(Service, blank=True, null=True)
	status = models.BooleanField(default=True, null=False)

	def __unicode__(self):
		return '%s' % (self.name)

	def save(self, *args, **kwargs):
		''' On save, update timestamps '''
		if not self.id:
			self.created = datetime.today()
		self.modified = datetime.today()
		super(Company, self).save(*args, **kwargs)

	def dump_to_dict(self, full=False):
		response = {
			'id': self.pk,
			'name': self.name,
			'created': self.created.strftime("%Y-%m-%d"),
			'modified': self.modified.strftime("%Y-%m-%d"),
			'status': ("Inactive", "Active")[self.status],
		}

		if full:
			response.update({
				'website': self.website,
				'address1': self.address1,
				'address2': self.address2,
				'city': self.city,
				'state': self.state,
				'zip': self.zip,
				'phone': self.phone,
				'fax': self.fax,
				'description': self.description
			})

		return response

def search(query):
	return Company.objects.filter(name__icontains=query)
