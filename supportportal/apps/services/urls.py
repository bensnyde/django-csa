from django.conf.urls import patterns, url
from apps.services import views

urlpatterns = patterns('',
    # Views
    url(r'^$', views.index, name='index'),
)
