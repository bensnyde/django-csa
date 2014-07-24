from django import forms

class EmailForm(forms.Form):
	email = forms.EmailField()

class ChpwForm(EmailForm):
	password = forms.CharField(max_length=128)

class AddPopForm(EmailForm):
	password = forms.CharField(max_length=128)
	quota = forms.IntegerField()

class AddForwardForm(forms.Form):
	FWDOPTS = (
		('fail', 'Fail'),
		('fwd', 'Forward'),
		('system', 'System'),
		('blackhole', 'Blackhole'),
		('pipe', 'Pipe')
	)

	email = forms.EmailField()
	fwdopt = forms.ChoiceField(choices=FWDOPTS)
	fwdemail = forms.EmailField(required=False)
	fwdsystem = forms.SlugField(required=False)
	failmsgs = forms.CharField(max_length=512, required=False)
	pipefwd = forms.CharField(max_length=512, required=False)

class SetQuotaForm(EmailForm):
	quota = forms.IntegerField()