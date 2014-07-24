from django.conf.urls import patterns, url
from news import views

urlpatterns = patterns('',
    # AJAX
    url(r'^get/$', views.get_news, name='getnews'),
    url(r'^set/$', views.set_news, name='setnews'),
    url(r'^del/$', views.delete_news, name='delnews'),
)
