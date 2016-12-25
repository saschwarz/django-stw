from django.conf.urls import patterns, url
from django.views.generic import TemplateView

# this hooks up the example html file
urlpatterns = patterns('',
                       url(r'',
                           TemplateView.as_view(template_name='stwexample.html'),
                           ),
                       )
