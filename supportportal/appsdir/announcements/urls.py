from django.conf.urls import patterns, url
from appsdir.announcements import views


urlpatterns = patterns('',
    url(r'^(?P<announcement_id>\d+)/$', views.detail, name='detail'),
    url(r'^$', views.index, name='index'),
)