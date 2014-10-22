from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
     # General
     url(r'^$', 'apps.dashboard.views.index', name='dashboard'),
     url(r'^search/', include('apps.search.urls', namespace="search")),
     # Support
     url(r'^support/tickets/', include('apps.support.tickets.urls', namespace="tickets")),
     url(r'^support/kb/', include('apps.support.knowledgebase.urls', namespace="knowledgebase")),
     url(r'^support/contact/', include('apps.support.contact.urls', namespace="contact")),
     # couplers
     url(r'^services/ip/', include('apps.ip.urls', namespace="ip")),
     url(r'^services/dns/', include('apps.dns.urls', namespace="dns")),
     url(r'^services/solusvm/', include('apps.solusvm.urls', namespace="solusvm")),
     url(r'^services/vmware/', include('apps.vmware.urls', namespace="vmware")),
     url(r'^services/email/', include('apps.email.urls', namespace="email")),
     url(r'^services/ftp/', include('apps.ftp.urls', namespace="ftp")),
     url(r'^services/domain/', include('apps.opensrs.urls', namespace="domain")),
     url(r'^services/server/', include('apps.servers.urls', namespace="servers")),
     url(r'^services/zenoss/', include('apps.zenoss.urls', namespace="zenoss")),
     url(r'^services/', include('apps.services.urls', namespace="services")),
     # Accounts
     url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'registration/login.html'}, name='login'),
     url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login/'}),
     url(r'^accounts/contact/', include('apps.contacts.urls', namespace="contacts")),
     url(r'^accounts/company/', include('apps.companies.urls', namespace="companies")),
     # Backend
     url(r'^root/', include('apps.backend.urls', namespace="backend")),
     url(r'^announcements/', include('apps.announcements.urls', namespace="announcements")),
     url(r'^reports/', include('apps.reports.urls', namespace="reports")),
     url(r'^affiliates/', include('apps.affiliates.urls', namespace="affiliates")),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
