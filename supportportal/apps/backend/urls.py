from django.conf.urls import patterns, url
from apps.backend import views

urlpatterns = patterns('',
    # Views
    url(r'^$', views.index, name='index'),
)
