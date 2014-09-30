from apps.ip import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
     # Views
     url(r'^$', views.index, name='index'),
     url(r'^(?P<parent>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/$', views.index, name='index'),
     url(r'^admin/$', views.admin, name='admin'),
     url(r'^request/$', views.request_ip_space, name='request_space'),
     # AJAX
     url(r'^getnetwork/$', views.get_network, name='getnetwork'),
     url(r'^getnetworks/$', views.get_networks, name='getnetworks'),
     url(r'^getnetworkusable/$', views.get_network_usable_hosts, name='getnetworkusable'),
     url(r'^gethosts/$', views.get_hosts, name='gethosts'),
     url(r'^gethost/$', views.get_host_details, name='gethost'),
     url(r'^sethost/$', views.set_host_details, name='sethost'),
     url(r'^setnetwork/$', views.set_network, name='setnetwork'),
     url(r'^getvlan/$', views.get_vlan, name='getvlan'),
     url(r'^setvlan/$', views.set_vlan, name='setvlan'),
     url(r'^delvlan/$', views.delete_vlan, name='delvlan'),
     url(r'^getvrf/$', views.get_vrf, name='getvrf'),
     url(r'^setvrf/$', views.set_vrf, name='setvrf'),
     url(r'^delvrf/$', views.delete_vrf, name='delvrf'),
     url(r'^truncate/$', views.truncate_network, name='truncate'),
     url(r'^split/$', views.split_network, name='split'),
     url(r'^getsplitopts/$', views.get_split_network_options, name='getsplitopts'),
     url(r'^resize/$', views.resize_network, name='resize'),
     url(r'^delnetwork/$', views.delete_network, name='delnetwork'),
)
