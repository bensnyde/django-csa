from django.conf.urls import patterns, url
from apps.support.tickets import views

urlpatterns = patterns('',
    # Views
    url(r'^index/$', views.index, name='index'),
    url(r'^detail/(?P<ticket_id>\d+)/$', views.detail, name='detail'),
    url(r'^admin/$', views.admin, name='admin'),
    # AJAX
    url(r'^list/$', views.get_tickets, name='gettickets'),
    url(r'^create/$', views.create_ticket, name='create_ticket'),
    url(r'^create/(?P<service_id>\d+)/$', views.create_ticket, name='create_ticket'),
    url(r'^posts/(?P<ticket_id>\d+)/$', views.get_posts, name='getposts'),
    url(r'^get/(?P<ticket_id>\d+)/$', views.get_ticket, name='getticket'),
    url(r'^set/(?P<ticket_id>\d+)/$', views.set_ticket, name='setticket'),
    url(r'^reply/(?P<ticket_id>\d+)/$', views.create_post, name='setpost'),
    url(r'^contacts/(?P<ticket_id>\d+)/$', views.set_contacts, name='set_contacts'),
    url(r'^visibility/(?P<post_id>\d+)/$', views.toggle_visibility, name='togglevisibility'),
    url(r'^satisfaction/(?P<ticket_id>\d+)/$', views.set_satisfaction_rating, name='setsatisfaction'),
    url(r'^summary/$', views.get_summary, name='summary'),
    url(r'^getqueue/$', views.get_queue, name='getqueue'),
    url(r'^setqueue/$', views.set_queue, name='setqueue'),
    url(r'^delqueue/$', views.delete_queue, name='delqueue'),
    url(r'^getmacros/$', views.get_macros, name='getmacros'),
    url(r'^setmacro/$', views.set_macro, name='setmacro'),
    url(r'^delmacro/$', views.delete_macro, name='delmacro'),
)
