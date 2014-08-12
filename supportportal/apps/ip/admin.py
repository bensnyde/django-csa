from django.contrib import admin
from .models import NetworkAddress, IPAddress, Vlan, Vrf

admin.site.register(NetworkAddress)
admin.site.register(IPAddress)
admin.site.register(Vlan)
admin.site.register(Vrf)
