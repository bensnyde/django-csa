from django import forms

class DateForm(forms.Form):
	startdate = forms.DateField(required=False, input_formats=['%Y-%m-%d'])
	enddate = forms.DateField(required=False, input_formats=['%Y-%m-%d'])