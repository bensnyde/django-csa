from django.conf.urls import patterns, url
from appsdir.reports import views

urlpatterns = patterns('',
    url(r'^index/$', views.index, name='index'),
)