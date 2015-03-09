from django.apps import AppConfig

class LoggersConfig(AppConfig):
    name = 'appsdir.loggers'

    def ready(self):
        import appsdir.loggers.signals