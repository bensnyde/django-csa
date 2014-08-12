from django.conf.urls import patterns, url
from apps.support.knowledgebase import views

urlpatterns = patterns('',
    # Views
    url(r'^$', views.index, name='index'),
    url(r'^admin/$', views.admin, name='admin'),
    url(r'^admin/(?P<article_id>\d+)/$$', views.admin, name='admin'),
    url(r'^(?P<article_id>\d+)/$', views.detail, name='detail'),
    # AJAX
    url(r'^getsummary/$', views.get_summary, name='getsummary'),
    url(r'^getarticle/(?P<article_id>\d+)/$', views.get_article, name='getarticle'),
    url(r'^setarticle/$', views.set_article, name='setarticle'),
    url(r'^delarticle/$', views.delete_article, name='delarticle'),
    url(r'^settag/$', views.set_tag, name='settag'),
    url(r'^gettags/$', views.get_tags, name='gettags'),
    url(r'^deltag/$', views.delete_tag, name='deltag'),
    url(r'^delcategory/$', views.delete_category, name='delcategory'),
    url(r'^setcategory/$', views.set_category, name='setcategory'),
    url(r'^getcategories/$', views.get_categories, name='getcategories'),
)
