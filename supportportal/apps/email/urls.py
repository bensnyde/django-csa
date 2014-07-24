from django.conf.urls import patterns, url
from apps.email import views

urlpatterns = patterns('',
    # Views
    url(r'^(?P<service_id>\d+)/$', views.index, name='index'),
    # AJAX
    url(r'^getaccounts/(?P<service_id>\d+)/$', views.getaccounts, name='getaccounts'),
    url(r'^getforwards/(?P<service_id>\d+)/$', views.getforwards, name='getforwards'),
    url(r'^createacct/(?P<service_id>\d+)/$', views.createaccount, name='addacct'),
    url(r'^createfwd/(?P<service_id>\d+)/$', views.createforward, name='addfwd'),
    url(r'^createdomfwd/(?P<service_id>\d+)/$', views.createdomainforward, name='adddomfwd'),
    url(r'^delacct/(?P<service_id>\d+)/$', views.delaccount, name='delacct'),
    url(r'^chpw/(?P<service_id>\d+)/$', views.chpw, name='chpw'),
    url(r'^setquota/(?P<service_id>\d+)/$', views.setquota, name='setquota'),
)
