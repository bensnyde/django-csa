from django.conf.urls import patterns, url
from appsdir.knowledgebase import views

urlpatterns = patterns('',
    # Views
    url(r'^index/$', views.index, name='index'),
    url(r'^index/(?P<category_id>\d+)/$', views.index, name='index'),
    url(r'^index/(?P<category_id>\d+)/(?P<tag_id>\d+)/$', views.index, name='index'),
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^admin/(?P<article_id>\d+)/$$', views.admin, name='admin'),
    url(r'^detail/(?P<article_id>\d+)/$', views.detail, name='detail'),
)
