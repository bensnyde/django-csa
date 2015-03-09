from django.conf.urls import patterns, include, url
from django.conf import settings
from api import router

urlpatterns = patterns('',
    url('^activity/', include('actstream.urls')),
    url('^dashboard/', include('appsdir.dashboard.urls', namespace='dashboard')),
    url('^search/', include('appsdir.search.urls', namespace='search')),
    url('^support/', include('appsdir.support.urls', namespace='tickets')),
    url('^knowledgebase/', include('appsdir.knowledgebase.urls', namespace='knowledgebase')),
    url('^login/', 'django.contrib.auth.views.login', {'template_name': 'registration/login.html'}, name='login'),
    url('^logout/', 'django.contrib.auth.views.logout', {'next_page': '/login/'}),
    url('^accounts/contact/', include('appsdir.contacts.urls', namespace='contacts')),
    url('^accounts/company/', include('appsdir.companies.urls', namespace='companies')),
    url('^reports/', include('appsdir.reports.urls', namespace='reports')),
    url('^groups/', include('appsdir.groups.urls', namespace='groups')),
    url('^announcements/', include('appsdir.announcements.urls', namespace='announcements')),
    url('^api/', include(router.urls)),
    url('^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('^$', 'django.contrib.auth.views.login', {'template_name': 'registration/login.html'}, name='login'),
)

if settings.DEBUG:
    urlpatterns += patterns('', ('^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))