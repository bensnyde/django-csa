from django.conf.urls import patterns, url
from appsdir.search import views

urlpatterns = patterns('',
    url(r'^results/', views.results, name='results'),
)