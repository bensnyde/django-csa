from django.contrib import admin
from .models import ActionLogger, AuthenticationLogger, ErrorLogger

admin.site.register(ActionLogger)
admin.site.register(AuthenticationLogger)
admin.site.register(ErrorLogger)
