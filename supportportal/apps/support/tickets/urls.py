from django.conf.urls import patterns, url
from apps.support.tickets import views

urlpatterns = patterns('',
    # Views
    url(r'^$', views.index, name='index'),
    url(r'^(?P<ticket_id>\d+)/$', views.detail, name='detail'),
    # AJAX
    url(r'^summary/$', views.get_summary, name='summary'),
    url(r'^gettickets/$', views.get_company_tickets, name='gettickets'),
    url(r'^getticket/(?P<ticket_id>\d+)/$', views.get_ticket, name='getticket'),
    url(r'^create_ticket/$', views.create_ticket, name='create_ticket'),
    url(r'^create_ticket/(?P<service_id>\d+)/$', views.create_ticket, name='create_ticket'),
    url(r'^create_post/$', views.set_post, name='setpost'),
    url(r'^set_contacts/$', views.set_contacts, name='set_contacts'),
    url(r'^toggleflag/$', views.toggle_flag, name='toggleflag'),
    url(r'^togglevisibility/$', views.toggle_visibility, name='togglevisibility'),
)
