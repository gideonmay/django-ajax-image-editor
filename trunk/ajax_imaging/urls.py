from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^(?P<id>[0-9]+)/$', view='ajax_imaging.views.main', name='image_editor_main'),
    url(r'^uploadImage/$', view='ajax_imaging.views.upload', name='image_editor_upload'),    
    url(r'^(?P<id>[0-9]+)/getImage/', view='ajax_imaging.views.get_image', name='image_editor_get_image'),        
    url(r'^(?P<id>[0-9]+)/processImage/', view='ajax_imaging.views.process_image', name='image_editor_process_image'),        
    url(r'^myarch/$', view='ajax_imaging.views.image_list', name='my_image_archive'),
)
