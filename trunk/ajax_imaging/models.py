from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Image(models.Model):
    IMAGE_STATUS = (
	(0,'restricted'),
	(1,'aproved'),
    )

    def user_image_folder(self, filename):
	return 'uploads/'+self.user.username+'/image_archive/'+filename

    #'uploads/ajax_imaging/'
    user = models.ForeignKey(User, related_name='images', editable=False)
    data = models.ImageField('Image',upload_to=user_image_folder, help_text='the size of the uploaded file must not be greater than 2.5mb')
    content_type = models.CharField(max_length=100,editable=False)
    width = models.IntegerField(editable=False)
    height = models.IntegerField(editable=False)
    status = models.IntegerField(choices=IMAGE_STATUS, editable=False)
