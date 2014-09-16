from django.conf.urls import patterns, url
from apps.companies import views

urlpatterns = patterns('',
    # Views
    url(r'^(?P<company_id>\d+)/$', views.detail, name='detail'),
    url(r'^$', views.index, name='index'),
    # AJAX
    url(r'^index/$', views.get_companies, name='getcompanies'),
    url(r'^detail/(?P<company_id>\d+)/$', views.get, name='get'),
    url(r'^set/(?P<company_id>\d+)/$', views.set, name='set'),
    url(r'^services/$', views.get_services, name='getservices'),
    url(r'^feeds/(?P<company_id>\d+)/$', views.get_feeds, name='getfeeds'),
    url(r'^contacts/(?P<company_id>\d+)/$', views.get_contacts, name='getcontacts'),
)
