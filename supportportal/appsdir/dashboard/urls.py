from django.conf.urls import patterns, url
from appsdir.dashboard import views

urlpatterns = patterns('',
    url(r'^index/', views.index, name='index'),
    url(r'^contactus/', views.contactus, name='contactus'),
)