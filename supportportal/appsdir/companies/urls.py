from django.conf.urls import patterns, url
from appsdir.companies import views


urlpatterns = patterns('',
    url(r'^(?P<company_id>\d+)/$', views.detail, name='detail'),
    url(r'^$', views.index, name='index'),
)