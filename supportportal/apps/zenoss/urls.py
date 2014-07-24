from django.conf.urls import patterns, url
from apps.zenoss import views

urlpatterns = patterns('',
    # Index
    url(r'^getinterfacegraphs/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.get_interface_graphs, name='getgraphs'),
    url(r'^getinterfacedetails/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.get_interface_details, name='getdetails'),
    url(r'^getinterfaceevents/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.get_interface_events, name='getevents'),
)
