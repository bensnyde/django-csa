from django.conf.urls import patterns, url
from apps.contacts import views

urlpatterns = patterns('',
    url(r'^index/$', views.index, name="index"),
    url(r'^detail/(?P<user_id>\d+)/$', views.detail, name="detail"),
    url(r'^get/(?P<user_id>\d+)/$', views.get, name="get"),
    url(r'^set/$', views.set, name="set"),
    url(r'^create/$', views.create, name="create"),
    url(r'^chpw/$', views.chpw, name="chpw"),
    url(r'^getlogs/(?P<user_id>\d+)/$', views.get_logs, name="getlogs"),
)
