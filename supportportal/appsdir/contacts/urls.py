from django.conf.urls import patterns, url
from appsdir.contacts import views


urlpatterns = patterns('',
    url(r'^index/$', views.index, name="index"),
    url(r'^detail/(?P<contact_id>\d+)/$', views.detail, name="detail"),
)
