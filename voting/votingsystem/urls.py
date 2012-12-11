from django.conf.urls.defaults import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^stages/', include('stages.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^', include("votingsystem.sondages.urls")),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '../static'}),

    (r'^files/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': './files'}),

)

