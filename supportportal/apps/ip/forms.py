from django import forms
from django.forms import ModelForm
from django.db import models
from .models import NetworkAddress, IPAddress, Vlan, Vrf

class NetworkAddressAddForm(ModelForm):
    class Meta:
        model = NetworkAddress


class IPAddressForm(ModelForm):
	ptr = forms.CharField(required=False) # ADD VALIDATION
	network = forms.CharField()

	class Meta:
		model = IPAddress
		fields = ('address', 'description')

class NetworkAddressForm(forms.Form):
    parent = forms.CharField(max_length=256)

class VlanForm(ModelForm):
    class Meta:
        model = Vlan

class VrfForm(ModelForm):
    class Meta:
        model = Vrf

class ResizeNetworkForm(forms.Form):
    networkaddress_id = forms.IntegerField(min_value=0, max_value=32)
    new_cidr = forms.IntegerField(min_value=0, max_value=32)
    group_under = forms.BooleanField(required=False)