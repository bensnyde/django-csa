from django.conf.urls import patterns, url
from apps.support.tickets import views

urlpatterns = patterns('',
    # Views
    url(r'^$', views.index, name='index'),
    url(r'^(?P<ticket_id>\d+)/$', views.detail, name='detail'),
    url(r'^admin/$', views.admin, name='admin'),
    # AJAX
    url(r'^summary/$', views.get_summary, name='summary'),
    url(r'^getqueue/$', views.get_queue, name='getqueue'),
    url(r'^setqueue/$', views.set_queue, name='setqueue'),
    url(r'^delqueue/$', views.delete_queue, name='delqueue'),
    url(r'^gettickets/$', views.get_tickets, name='gettickets'),
    url(r'^get/(?P<ticket_id>\d+)/$', views.get_ticket, name='getticket'),
    url(r'^create/$', views.create_ticket, name='create_ticket'),
    url(r'^create/(?P<service_id>\d+)/$', views.create_ticket, name='create_ticket'),
    url(r'^reply/$', views.set_post, name='setpost'),
    url(r'^contacts/$', views.set_contacts, name='set_contacts'),
    url(r'^flag/$', views.toggle_flag, name='toggleflag'),
    url(r'^visibility/$', views.toggle_visibility, name='togglevisibility'),
)
