from django import forms
from django.forms import ModelForm
from .models import Queue, Ticket, Post, Macro


class QueueForm(ModelForm):
    class Meta:
        model = Queue

class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['contacts', 'queue', 'priority', 'service', 'due_date', 'description']

class TicketContactsForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['contacts']

class TicketSatisfactionForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['satisfaction_rating']

class AdminSetTicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['contacts', 'description', 'queue', 'priority', 'service', 'author', 'due_date', 'staff_summary', 'difficulty_rating', 'status']

class AdminCreateTicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ['description', 'queue', 'priority', 'service', 'author', 'due_date']

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['contents', 'attachment']
        ordering = ['date']

class PostAttachmentForm(ModelForm):
    class Meta:
        model = Post
        fields = ['attachment']

class PostVisibilityForm(ModelForm):
    class Meta:
        model = Post
        fields = ['visible']

class PostRatingForm(ModelForm):
    class Meta:
        model = Post
        fields = ['rating']

class MacroForm(ModelForm):
    class Meta:
        model = Macro
        exclude = ['date', 'author']