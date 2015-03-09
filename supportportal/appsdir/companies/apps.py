from django.apps import AppConfig
from actstream import registry
import watson

class CompaniesConfig(AppConfig):
    name = 'appsdir.companies'

    def ready(self):
        Company = self.get_model('Company')
        watson.register(Company)
        registry.register(Company)