from django.conf.urls import patterns, url
from apps.servers import views

urlpatterns = patterns('',
    # Views
    url(r'^(?P<service_id>\d+)/$', views.index, name='index'),
    url(r'^(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.detail, name='detail'),
    # AJAX
    url(r'^getservers/(?P<service_id>\d+)/$', views.get_servers, name='getservers'),
    url(r'^get/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.get_server, name='getserver'),
    url(r'^del/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.delete_server, name='delserver'),
    url(r'^set/(?P<service_id>\d+)/$', views.set_server, name='setserver'),
)
