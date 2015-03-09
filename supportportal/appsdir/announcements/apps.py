from django.apps import AppConfig
from actstream import registry
import watson


class AnnouncementsConfig(AppConfig):
    name = 'appsdir.announcements'

    def ready(self):
        Announcement = self.get_model('Announcement')
        watson.register(Announcement)
        registry.register(Announcement)