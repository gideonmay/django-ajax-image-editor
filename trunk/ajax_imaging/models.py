from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from utils import slugify
from sorl.thumbnail.main import DjangoThumbnail
import os

# Create your models here.
class Image(models.Model):
    IMAGE_STATUS = (
    	(0,'restricted'),
    	(1,'aproved'),
    )

    def user_image_folder(self, filename):
        return 'upload'+os.sep+self.user.username+os.sep+'image_archive'+os.sep+filename

    #'uploads/ajax_imaging/'
    user = models.ForeignKey(User, related_name='images', editable=False)
    data = models.ImageField('Image',upload_to=user_image_folder, help_text='the size of the uploaded file must not be greater than 2.5mb')
    content_type = models.CharField(max_length=100,editable=False)
    width = models.IntegerField(editable=False)
    height = models.IntegerField(editable=False)
    status = models.IntegerField(choices=IMAGE_STATUS, editable=False)
    
    def get_filename(self):
        return os.path.basename(self.data.url)

    def get_size(self):
        return int(self.data.size/1024.0)

    def get_thumb_url(self):
        return DjangoThumbnail(self.data,(96,96),["crop","upscale"]).relative_url
    
    def save(self):
        super(Image,self).save()

    def __unicode__(self):
        str = os.path.basename(self.data.url)
        return str
