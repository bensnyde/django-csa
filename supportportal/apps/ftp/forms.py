from django import forms

class AddFtpForm(forms.Form):
	username = forms.SlugField() 
	password = forms.CharField(max_length=256)
	password_confirm = forms.CharField(max_length=256)
	quota = forms.IntegerField(required=False)
	homedir = forms.CharField(max_length=256, required=False)

class SetQuotaForm(forms.Form):
	username = forms.SlugField() 
	quota = forms.IntegerField()

class ChpwForm(forms.Form):
	username = forms.SlugField() 
	password = forms.CharField(max_length=256)
	password_confirm = forms.CharField(max_length=256)

class DelFtpForm(forms.Form):
	username = forms.SlugField() 
	destroy = forms.BooleanField(required=False)	