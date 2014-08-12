from django.conf.urls import patterns, url
from apps.companies import views

urlpatterns = patterns('',
    # Views
    url(r'^(?P<company_id>\d+)/$', views.detail, name='detail'),
    url(r'^$', views.index, name='index'),
    # AJAX
    url(r'^get/(?P<company_id>\d+)/$', views.get, name='get'),
    url(r'^getservices/$', views.get_services, name='getservices'),
    url(r'^getcompanies/$', views.get_companies, name='getcompanies'),
    url(r'^getfeeds/(?P<company_id>\d+)/$', views.get_feeds, name='getfeeds'),
    url(r'^getcontacts/(?P<company_id>\d+)/$', views.get_contacts, name='getcontacts'),
    url(r'^set/(?P<company_id>\d+)/$', views.set, name='set'),
)
