from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('imgallery.views',
    url(r'^$', view='my_folder_list', name='my_image_folders'),
    #url(r'^v2/$', view='my_folder_list', kwargs={'template_name' : "imgallery/folder-list-v2.html"}, name='my_image_folders_v2'),
    url(r'^new-gallery/$', view='create_gallery', kwargs={'type':'photo'}, name='create_photo_gallery'),
    url(r'^new-article-gallery/$', view='create_gallery', kwargs={'type':'article'}, name='create_article_gallery'),
    url(r'^(?P<id>[0-9]+)/$', view='photo_gallery_details', name='photo_gallery_by_id')
)
