from django import forms

class DomainForm(forms.Form):
	domain = forms.CharField(max_length=100)

class DomainRegisterForm(DomainForm):
	owner = forms.CharField(max_length=100)
	period = forms.IntegerField(max_value=4)
	username = forms.CharField(max_length=100)
	password = forms.CharField(max_length=100)
	auto_renew = forms.BooleanField()
