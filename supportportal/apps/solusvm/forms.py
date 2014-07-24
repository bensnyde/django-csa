from django import forms

class BootOrderForm(forms.Form):
	bootorder = forms.ChoiceField(choices=[('cd', 'cd'), ('dc', 'dc'), ('c', 'c'), ('d', 'd')])

class HostnameForm(forms.Form):
	hostname = forms.CharField(max_length=200)

class MountISOForm(forms.Form):
	iso = forms.CharField(max_length=256)
