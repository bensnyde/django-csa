from django.conf.urls import patterns, url
from appsdir.groups import views


urlpatterns = patterns('', 
    url('^$', views.index, name='index'),
)
