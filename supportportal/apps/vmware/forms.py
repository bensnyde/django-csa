from django import forms

class MountISOForm(forms.Form):
    iso = forms.CharField(max_length=256)


class SnapshotPathForm(forms.Form):
    path = forms.CharField(max_length=256)

class CreateSnapshotForm(forms.Form):
	name = forms.CharField(max_length=64)
	description = forms.CharField(max_length=256)