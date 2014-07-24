from django.conf.urls import patterns, url
from apps.ftp import views

urlpatterns = patterns('',
    # Views
    url(r'^(?P<service_id>\d+)/$', views.index, name='index'),
    # AJAX
    url(r'^createacct/(?P<service_id>\d+)/$', views.createaccount, name='addacct'),
    url(r'^delacct/(?P<service_id>\d+)/$', views.delaccount, name='delacct'),
    url(r'^chpw/(?P<service_id>\d+)/$', views.chpw, name='chpw'),
    url(r'^setquota/(?P<service_id>\d+)/$', views.setquota, name='setquota'),
    url(r'^getaccounts/(?P<service_id>\d+)/$', views.get_accounts, name='getaccounts'),
    url(r'^getsessions/(?P<service_id>\d+)/$', views.get_sessions, name='getsessions'),
)
