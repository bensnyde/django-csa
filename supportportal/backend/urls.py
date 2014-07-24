from django.conf.urls import patterns, url
from backend import views

urlpatterns = patterns('',
    # Views
    url(r'^$', views.index, name='index'),
)
