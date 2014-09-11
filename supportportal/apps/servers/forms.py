from django import forms
from django.forms import ModelForm
from .models import Server

class ServerAdminForm(ModelForm):
       class Meta:
               model = Server
               exclude = ['created', 'modified']

class ServerClientForm(ModelForm):
       class Meta:
               model = Server
               fields = ['name', 'ip', 'os', 'username', 'password', 'notes']