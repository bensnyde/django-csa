from django.apps import AppConfig
from django.contrib.auth.models import Group
from actstream import registry


class GroupsConfig(AppConfig):
    name = 'appsdir.groups'

    def ready(self):
        registry.register(Group)
