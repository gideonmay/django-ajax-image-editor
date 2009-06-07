from django import forms
from ajax_imaging.models import Image

class ImageForm(forms.ModelForm):
    class Meta:
	model = Image