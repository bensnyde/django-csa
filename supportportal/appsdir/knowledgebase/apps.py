from django.apps import AppConfig
from actstream import registry
import watson

class KnowledgebaseConfig(AppConfig):
    name = 'appsdir.knowledgebase'

    def ready(self):
        Article = self.get_model('Article')
        Category = self.get_model('Category')
        Tag = self.get_model('Tag')

        watson.register(Article)
        watson.register(Category)
        watson.register(Tag)

        registry.register(Article)
        registry.register(Category)
        registry.register(Tag)
