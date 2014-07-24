from django.conf.urls import patterns, url
from apps.services import views

urlpatterns = patterns('',
    # Views
    url(r'^$', views.index, name='index'),
    url(r'^(?P<service_id>[\d]+)/detail/(?P<zone>[a-zA-Z_0-9.-]+)/$', views.detail, name='detail'),
    # AJAX
    url(r'^(?P<service_id>[\d]+)/deletezone/$', views.index, name='deletezone'),
)
