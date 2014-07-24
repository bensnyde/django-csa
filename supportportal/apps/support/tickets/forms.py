from django import forms
from django.forms import ModelForm, SelectMultiple
from .models import Ticket, Post

class TicketIDForm(forms.Form):
	ticket_id = forms.IntegerField()

class PostIDForm(forms.Form):
	post_id = forms.IntegerField()

class PostForm(ModelForm):
       class Meta:
               model = Post
               fields = ['contents', 'attachment']
               ordering = ['date']

class TicketForm(ModelForm):
       class Meta:
               model = Ticket
               fields = ['contacts', 'description']