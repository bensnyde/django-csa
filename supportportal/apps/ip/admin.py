from django.contrib import admin
from .models import NetworkAddress, IPAddress

admin.site.register(NetworkAddress)
admin.site.register(IPAddress)
