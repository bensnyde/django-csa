from apps.ip import views
from django.conf.urls import patterns, url

urlpatterns = patterns('',
     # Views
     url(r'^(?P<service_id>\d+)/$', views.index, name='index'),
     url(r'^(?P<service_id>\d+)/(?P<parent>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/$', views.index, name='index'),
     url(r'^request/', views.request_ip_space, name='request_space'),
     # AJAX
     url(r'^getnetworks/(?P<service_id>\d+)/$', views.get_networks, name='getnetworks'),
     url(r'^gethosts/(?P<service_id>\d+)/$', views.get_hosts, name='gethosts'),
     url(r'^gethost/(?P<service_id>\d+)/$', views.get_host_details, name='gethost'),
     url(r'^sethost/(?P<service_id>\d+)/$', views.set_host_details, name='sethost'),
     url(r'^setnetwork/(?P<service_id>\d+)/$', views.set_network, name='setnetwork'),
)
