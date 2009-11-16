from django.db import models
from django.contrib.auth.models import User
from ajax_imaging.models import Image
from imgallery.managers import FolderManager
from django.utils.translation import ugettext_lazy as _
from news.models import News
from utils import slugify
from django.conf import settings
import os

class Folder(models.Model):
    FOLDER_CHOICE = (
        (0, _('Default')),
        (1, _('Photo gallery')),
        (2, _('Article gallery')),
    )
    user = models.ForeignKey(User, editable=False, related_name='image_folders')
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=500, blank=True)
    slug = models.CharField(max_length=100, unique=True, editable=False)
    images = models.ManyToManyField(Image, related_name='folders', blank=True, null=True)
    public = models.BooleanField(default=True)
    type = models.IntegerField(_('type'),choices=FOLDER_CHOICE, default = 1)
    objects = FolderManager()
    
    def save(self):
        self.slug = slugify(self.name)
        super(Folder,self).save()
        
    def get_image(self):
        if self.images.count() == 0:
            if hasattr(settings, 'DEFAULT_IMAGE'):
                r = settings.DEFAULT_IMAGE
            else:
                r = 'picture_archive/default.jpg'
            return r
        else:
            return self.images.all()[0].data
    
    def get_type(self):
        if self.type == 1:
            return r'pgallery'
        elif self.type == 2:
            return r'agallery'
        else:
            return r'default'
        
#    def __unicode__(self):
#        return self.name
        
class ArticleFolder(Folder):
    """
    Article Folder 
    """
    news = models.ForeignKey(News, blank = True, null = True)
    
    def save(self):
        self.type = 2
        super(ArticleFolder, self).save()