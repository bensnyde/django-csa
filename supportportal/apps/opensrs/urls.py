from django.conf.urls import patterns, url
from apps.opensrs import views

urlpatterns = patterns('',
    # Index
    url(r'^(?P<domain>[a-zA-Z_0-9.-]+)$', views.index, name='index'),
    url(r'^suggest/', views.name_suggest, name='suggest'),
    url(r'^check_transfer/', views.check_transfer, name='transfer'),
    url(r'^get_price/', views.get_domain_price, name='price'),
    url(r'^get_balance/', views.get_balance, name='balance'),
    url(r'^register/', views.register_domain, name='register'),
)
