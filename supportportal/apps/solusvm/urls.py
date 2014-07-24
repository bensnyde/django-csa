from django.conf.urls import patterns, url
from apps.solusvm import views

urlpatterns = patterns('',
    url(r'^boot/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.boot, name='boot'),
    url(r'^reboot/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.reboot, name='reboot'),
    url(r'^shutdown/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.shutdown, name='shutdown'),
    url(r'^mountiso/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.mount_iso, name='mount'),
    url(r'^hostname/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.set_hostname, name='set_hostname'),
    url(r'^setbootorder/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.set_bootorder, name='set_bootorder'),
    url(r'^getdetails/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.get_details, name='getdetails'),
    url(r'^getisos/(?P<service_id>\d+)/$', views.get_isos, name='getisos'),
)
