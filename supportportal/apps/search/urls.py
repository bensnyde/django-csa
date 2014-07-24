from django.conf.urls import patterns, url
from apps.search import views

urlpatterns = patterns('',
    url(r'^results/', views.results, name='results'),
)
