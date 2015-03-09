from django.forms import ModelForm
from .models import Company


class CompanyForm(ModelForm):
	class Meta:
		model = Company
		fields = ['name', 'description', 'address1', 'address2', 'city', 'state', 'zip', 'website', 'phone', 'fax']