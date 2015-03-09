from django.apps import AppConfig
from actstream import registry
from simple_history import register
import watson

class ContactsConfig(AppConfig):
    name = 'appsdir.contacts'

    def ready(self):
        Contact = self.get_model('Contact')
        watson.register(Contact)
        registry.register(Contact)
        register(Contact)