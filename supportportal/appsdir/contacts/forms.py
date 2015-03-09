from django.forms import ModelForm
from django import forms
from .models import Contact


class ContactForm(ModelForm):
	class Meta:
		model = Contact
		exclude = ['last_login', 'created', 'company', 'is_superuser', 'user_permissions', 'groups']
		unique_together = ['email', 'company']

class ContactCreationForm(ModelForm):
	class Meta:
		model = Contact
		exclude = ['last_login', 'created', 'company', 'is_active', 'is_superuser']
		unique_together = ['email', 'company']

class ContactAdminForm(ModelForm):
	class Meta:
		model = Contact
		exclude = ['last_login', 'created', 'is_superuser']