from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

# this hooks up the example html file
urlpatterns = patterns('',
                       url(r'',
                           direct_to_template, {'template':'stwexample.html'},
                           ),
                       )
