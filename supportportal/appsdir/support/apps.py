from django.apps import AppConfig
from actstream import registry
import watson

class SupportConfig(AppConfig):
    name = 'appsdir.support'

    def ready(self):
        Queue = self.get_model('Queue')
        Ticket = self.get_model('Ticket')
        Post = self.get_model('Post')
        Macro = self.get_model('Macro')

        watson.register(Queue)
        watson.register(Ticket)
        watson.register(Post)
        watson.register(Macro)

        registry.register(Queue)
        registry.register(Ticket)
        registry.register(Post)
        registry.register(Macro)
