from django import forms
from django.forms import ModelForm
from .models import Queue, Ticket, Post, Macro
from appsdir.contacts.models import Contact


class QueueForm(ModelForm):
    class Meta:
        model = Queue
        exclude = ['changed_by']

class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['description', 'queue', 'priority', 'due_date', 'contacts']

class AdminCreateTicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['description', 'queue', 'priority', 'author', 'due_date']

class AdminSetTicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['description', 'queue', 'priority', 'author', 'owner', 'due_date', 'staff_summary', 'difficulty_rating', 'status', 'flagged']

    def __init__(self, *args, **kwargs):
        super(AdminSetTicketForm, self).__init__(*args, **kwargs)
        self.fields['owner'].queryset = Contact.objects.filter(company_id=0)

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['contents']
        ordering = ['created']

class MacroForm(ModelForm):
    class Meta:
        model = Macro
        exclude = ['created', 'modified', 'author']