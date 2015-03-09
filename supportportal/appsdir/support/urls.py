from django.conf.urls import patterns, url
from appsdir.support import views

urlpatterns = patterns('',
    url(r'^index/$', views.index, name='index'),
    url(r'^detail/(?P<ticket_id>\d+)/$', views.detail, name='detail'),
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^new/$', views.new, name='new'),
)