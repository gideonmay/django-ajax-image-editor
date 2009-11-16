from django import forms
from ajax_imaging.models import Image
import mimetypes, urllib

class ImageForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        super(ImageForm,self).__init__(*args,**kwargs)
        self.fields["file_count"] = forms.IntegerField(widget=forms.HiddenInput(), initial = 1)
        self.fields["folder"] = forms.IntegerField(widget=forms.HiddenInput(), initial = 0)
        
    class Meta:
    	model = Image
        
    def clean(self):
        file_count = int(self.cleaned_data.get("file_count", 0))
        if file_count < 4:
            return self.cleaned_data
        else:
            raise ValidationError("Too many pictures");
        
    
class ImageEditForm(forms.Form):
    image = forms.IntegerField(widget=forms.HiddenInput(),initial=0)
    action = forms.CharField(max_length=15,widget=forms.HiddenInput())
    save_as = forms.CharField(max_length=15,widget=forms.HiddenInput(),required=False) 
    resize_height = forms.IntegerField(widget=forms.HiddenInput(),required=False, initial=0)
    resize_width = forms.IntegerField(widget=forms.HiddenInput(),required=False,initial=0)
    left = forms.IntegerField(widget=forms.HiddenInput(),required=False, initial=0)
    top = forms.IntegerField(widget=forms.HiddenInput(),required=False,initial=0)
    right = forms.IntegerField(widget=forms.HiddenInput(),required=False,initial=0)
    bottom = forms.IntegerField(widget=forms.HiddenInput(),required=False,initial=0)
    degrees = forms.IntegerField(widget=forms.HiddenInput(),required=False,initial=0)
    display_height = forms.IntegerField(widget=forms.HiddenInput(),required=False,initial=0)
    display_width = forms.IntegerField(widget=forms.HiddenInput(),required=False,initial=0)
    
    def clean(self):
        cd = self.cleaned_data
        action = cd.get("action")
        if action not in ['rotate','crop','resize','save','save_as','view_original','view_active','undo']:
            raise forms.ValidationError("no such action")
        return cd