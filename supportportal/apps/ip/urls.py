from apps.ip import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
     # Views
     url(r'^(?P<service_id>\d+)/$', views.index, name='index'),
     url(r'^(?P<service_id>\d+)/(?P<parent>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/$', views.index, name='index'),
     url(r'^admin/$', views.admin, name='admin'),
     url(r'^request/$', views.request_ip_space, name='request_space'),
     # AJAX
     url(r'^getnetworks/(?P<service_id>\d+)/$', views.get_networks, name='getnetworks'),
     url(r'^gethosts/(?P<service_id>\d+)/$', views.get_hosts, name='gethosts'),
     url(r'^gethost/(?P<service_id>\d+)/$', views.get_host_details, name='gethost'),
     url(r'^sethost/(?P<service_id>\d+)/$', views.set_host_details, name='sethost'),
     url(r'^setnetwork/$', views.set_network, name='setnetwork'),
     url(r'^getvlan/$', views.get_vlan, name='getvlan'),
     url(r'^setvlan/$', views.set_vlan, name='setvlan'),
     url(r'^delvlan/$', views.delete_vlan, name='delvlan'),
     url(r'^getvrf/$', views.get_vrf, name='getvrf'),
     url(r'^setvrf/$', views.set_vrf, name='setvrf'),
     url(r'^delvrf/$', views.delete_vrf, name='delvrf'),
)
