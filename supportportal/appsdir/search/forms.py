from django import forms

class SearchForm(forms.Form):
	querystr = forms.CharField(max_length=64)
