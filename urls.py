from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from nexathan import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'nexathan.views.home', name='home'),
    # url(r'^nexathan/', include('nexathan.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('nexathan.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
