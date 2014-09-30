from django.forms import ModelForm
from django import forms
from .models import Contact

class ContactForm(ModelForm):
	class Meta:
		model = Contact
		exclude = ['last_login', 'password', 'created', 'company']
		unique_together = ['email', 'company']

class ContactCreationForm(ModelForm):
	class Meta:
		model = Contact
		exclude = ['last_login', 'created', 'company', 'is_active']
		unique_together = ['email', 'company']

class ContactAdminForm(ModelForm):
	class Meta:
		model = Contact
		exclude = ['last_login', 'created']

class ContactPasswordForm(forms.Form):
	old_password = forms.CharField()
	new_password = forms.CharField()
	confirm_password = forms.CharField()