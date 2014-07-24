from django import forms
from django.forms import ModelForm
from .models import Server

class ServerForm(ModelForm):
       class Meta:
               model = Server
               exclude = ['created', 'modified']