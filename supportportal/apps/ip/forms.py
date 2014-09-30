from django import forms
from django.forms import ModelForm
from django.db import models
from .models import NetworkAddress, IPAddress, Vlan, Vrf

class NetworkAddressForm(ModelForm):
    class Meta:
        model = NetworkAddress

class IPAddressForm(ModelForm):
	ptr = forms.CharField(required=False)
	network = forms.CharField()

	class Meta:
		model = IPAddress
		fields = ('address', 'description')

class VlanForm(ModelForm):
    class Meta:
        model = Vlan

class VrfForm(ModelForm):
    class Meta:
        model = Vrf

class NetworkAddressParentForm(forms.Form):
    parent = forms.CharField(max_length=256)

class ResizeNetworkForm(forms.Form):
    new_cidr = forms.IntegerField(min_value=0, max_value=32, initial=24)

class SplitNetworkForm(forms.Form):
    new_cidr = forms.IntegerField(min_value=0, max_value=32, widget=forms.Select())
    group_under = forms.BooleanField(required=False)