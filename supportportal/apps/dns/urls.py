from django.conf.urls import patterns, url
from apps.dns import views

urlpatterns = patterns('',
    # Views
    url(r'^(?P<service_id>[\d]+)/$', views.index, name='index'),
    url(r'^(?P<service_id>[\d]+)/detail/(?P<zone>[a-zA-Z_0-9.-]+)/$', views.detail, name='detail'),
    # AJAX
    url(r'^(?P<service_id>[\d]+)/getzones/$', views.getzones, name='getzones'),
    url(r'^(?P<service_id>[\d]+)/getrecords/$', views.getrecords, name='getrecords'),
    url(r'^(?P<service_id>[\d]+)/addrecord/$', views.addrecord, name='addrecord'),
    url(r'^(?P<service_id>[\d]+)/deleterecord/$', views.deleterecord, name='deleterecord'),
    url(r'^(?P<service_id>[\d]+)/createzone/$', views.createzone, name='createzone'),
    url(r'^(?P<service_id>[\d]+)/deletezone/$', views.deletezone, name='deletezone'),
)
