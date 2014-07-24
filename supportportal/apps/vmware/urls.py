from django.conf.urls import patterns, url
from apps.vmware import views

urlpatterns = patterns('',
    url(r'^reboot/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.reboot, name='reboot'),
    url(r'^boot/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.boot, name='boot'),
    url(r'^shutdown/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.shutdown, name='shutdown'),
    url(r'^mountiso/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.mount_iso, name='mount'),
    url(r'^createsnapshot/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.create_snapshot, name='createsnapshot'),
    url(r'^deletesnapshot/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.delete_snapshot, name='deletesnapshot'),
    url(r'^revertsnapshot/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.revert_snapshot, name='revertsnapshot'),
    url(r'^getstats/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.get_stats, name='getstats'),
    url(r'^getsnapshots/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.get_snapshots, name='getsnapshots'),
    url(r'^getisos/(?P<service_id>\d+)/(?P<server_id>\d+)/$', views.get_isos, name='getisos'),
)
