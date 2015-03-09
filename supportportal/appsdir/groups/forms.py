from django.forms import ModelForm
from django.contrib.auth.models import Group


class GroupForm(ModelForm):
    class Meta:
        model = Group
