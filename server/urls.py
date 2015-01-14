from django.conf.urls import patterns, include, url
from django.contrib import admin

from simpleapi import simple_api_patterns

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(simple_api_patterns)),
)
