from django.forms import ModelForm
from django import forms
from .models import Contact

class ContactForm(ModelForm):
	class Meta:
		model = Contact
		exclude = ['last_login', 'password', 'created', 'company', 'is_admin', 'is_active']
		unique_together = ['email', 'company']

class ContactPasswordForm(forms.Form):
	old_password = forms.CharField()
	new_password = forms.CharField()
	confirm_password = forms.CharField()