from extra.middleware.security import LOGIN
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('main.views',
    url(r'^$', 'index', name='index'),
    url(r'^complete/(?P<trans_id>[0-9a-z]+)/$', 'complete', name='complete'),
    url(r'^api/zip/(?P<country>[A-Za-z]{2})/(?P<zip>[0-9A-Za-z\-\_ ]+)/$', 'ajax_zip_lookup'),
    url(r'^no-site/$', 'no_site', name='no-site'),
)
