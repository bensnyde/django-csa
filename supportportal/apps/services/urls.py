from django.conf.urls import patterns, url
from apps.services import views

urlpatterns = patterns('',
    # Views
    url(r'^$', views.index, name='index'),
    # AJAX
    url(r'^get/$', views.get_services, name='getservices'),
)
