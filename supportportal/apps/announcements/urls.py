from django.conf.urls import patterns, url
from apps.announcements import views

urlpatterns = patterns('',
    # AJAX
    url(r'^index/$', views.get_index, name='getall'),
    url(r'^detail/$', views.get_detail, name='get'),
    url(r'^set/$', views.set, name='setnews'),
    url(r'^del/$', views.delete, name='delnews'),
)
