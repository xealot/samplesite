from extra.middleware.security import LOGIN
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('main.views',
    url(r'^$', 'index', name='index'),
    url(r'^signup/$', 'sign_up', name='signup'),
    url(r'^login/$', 'sign_in', name='login'),
    url(r'^logout/$', 'sign_out', name='logout'),
)

#Secure Locations
urlpatterns += patterns('main.views',
    url(r'^start/$', 'start', {LOGIN: True}, name='start'),
    url(r'^step/1/(?P<code>[0-9A-Za-z\-\_]+)/$', 'step_one', {LOGIN: True}, name='step_one'),
    url(r'^step/1/(?P<pending_id>\d+)/edit/$', 'step_one_edit', {LOGIN: True}, name='step_one_edit'),
    url(r'^step/1/(?P<pending_id>\d+)/validate/$', 'step_one_validate', {LOGIN: True}, name='step_one_validate'),
    url(r'^step/2/$', 'step_two', {LOGIN: True}, name='step_two'),
    url(r'^step/3/$', 'step_three', {LOGIN: True}, name='step_three'),
    url(r'^api/zip/(?P<country>[A-Za-z]{2})/(?P<zip>[0-9A-Za-z\-\_ ]+)/$', 'ajax_zip_lookup', {LOGIN: True}),

)
