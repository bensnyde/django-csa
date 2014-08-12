from django.contrib import admin
from .models import ActionLogger, AuthenticationLogger

admin.site.register(ActionLogger)
admin.site.register(AuthenticationLogger)
