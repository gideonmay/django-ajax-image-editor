'''
Created on 15.08.2009

@author: german
'''
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from imgallery.models import Folder, ArticleFolder 

class FolderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Folder
        exclude = ['type','user','images']
        
class ArticleFolderForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ArticleFolderForm, self).__init__(*args, **kwargs)
        self.fields['news'].widget = forms.HiddenInput()

    class Meta:
        model = ArticleFolder
        exclude = ['type','user','images']