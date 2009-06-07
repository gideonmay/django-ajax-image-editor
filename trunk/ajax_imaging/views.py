from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files import File
from ajax_imaging.models import Image
from ajax_imaging.forms import ImageForm
from settings import MEDIA_ROOT
import Image as PImage
import os
from subprocess import *
from ajax_imaging.getimageinfo import getImageInfo

def execute(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    p.wait()
    return (p.stdout, p.returncode)

@login_required
def image_list(request):
    if request.POST:
	delimg = request.POST.getlist('delimg[]')
	Image.objects.filter(id__in=delimg).delete()
	return HttpResponseRedirect(reverse('my_image_archive'))
    list = Image.objects.filter(user=request.user)
    f = ImageForm()
    c = RequestContext(request, {'list' : list, 'form': f})
    return render_to_response('ajax_imaging/list.html', c)

@login_required
def main(request,id=1):
    c = RequestContext(request)
    return render_to_response('ajax_imaging/index.html',c)

@login_required
def upload(request):
    if request.POST:
        img = request.FILES.get('data')
        content_type, width, height = getImageInfo(img.read())
        
	#validation
        if not img or not content_type:
            return HttpResponseRedirect('/imaging/')
	
        image = Image()
        image.user = request.user
	image.data = img
        if content_type == "image/jpeg":
            image.content_type = "image/jpeg"
#            image.output_encoding = images.JPEG
        else:
    	    # GIFs, etc. get converted to PNG since only JPEG and PNG are currently supported
            image.content_type = "image/png"
#            image.output_encoding = images.PNG
        image.width = width
        image.height = height
	if width>600:
	    image.status = 0
	else:
	    image.status = 1
	image.save()
	if request.POST.get('next','') != '':
    	    return HttpResponseRedirect(request.POST['next'])
	else:
    	    return HttpResponseRedirect(reverse('my_image_archive'))
	
	
@login_required
def get_image(request,id=1):
    if request.GET:
	try:
	    image = Image.objects.get(pk=id)
	    path = image.data.path
	    pdir = os.path.dirname(path)
	    filename = os.path.basename(path)
	    if not os.path.exists(pdir+'/edit/'):
		os.mkdir(pdir+'/edit/')
#	    if not os.path.exists(pdir+'/activ/'):
#		os.mkdir(pdir+'/activ/')
	    if not os.path.exists(pdir+'/undo/'):
		os.mkdir(pdir+'/undo/')
	    if not os.path.exists(pdir+'/edit/'+filename):
		execute('cp %(path)s %(pdir)s/edit/' % {'path':path, 'pdir':pdir})
#	    if not os.path.exists(pdir+'/activ/'+filename):
#		execute('cp %(path)s %(pdir)s/activ/' % {'path':path, 'pdir':pdir})
	    if not os.path.exists(pdir+'/undo/'+filename):
		execute('cp %(path)s %(pdir)s/undo/' % {'path':path, 'pdir':pdir})
	    f = open(pdir+'/edit/'+filename,"rb")
	    response = HttpResponse(f.read(), mimetype=image.content_type, content_type=image.content_type)
	    f.close()
	    return response
	except:
	    return None
	    
@login_required
def process_image(request,id=1):
    if request.GET:
        saved_image = Image.objects.get(pk=id)
#	if saved_image.user != request.user:
#	    return

        action = request.GET.get("action")
        
        if saved_image and action:            
	    path = saved_image.data.path
    	    pdir = os.path.dirname(path)
	    filename = os.path.basename(path)
	    if action not in ['undo','save','view_active','view_original','save_as']:
		execute('cp '+pdir+'/edit/'+filename+' '+pdir+'/undo/'+filename)
		
	    if action == "undo":
		execute('mv '+pdir+'/edit/'+filename+' '+pdir+'/edit/_'+filename)
		execute('mv '+pdir+'/undo/'+filename+' '+pdir+'/edit/'+filename)
		execute('mv '+pdir+'/edit/_'+filename+' '+pdir+'/undo/'+filename)
		return
	    elif action == "view_original":
		execute('cp '+path+' '+pdir+'/edit/'+filename)
		return
#	    elif action == "view_active":
#		execute('cp '+pdir+'/activ/'+filename+' '+pdir+'/edit/'+filename)
	    elif action == "save":
		execute('cp '+pdir+'/edit/'+filename+' '+path)
		im = PImage.open(path)
		saved_image.width = im.width
		saved_image.height = im.height
		saved_image.save()
		return
	    elif action == "save_as":
		fname = request.GET.get("fname")
		fname = os.path.basename(fname)
		k = fname.split(os.extsep)
		iext = filename.split(os.extsep)[-1].lower()
		ext = k[-1].lower()
		if (ext != iext):
		    if (ext == "jpg" or ext == "jpeg"):
			content_t = 'image/jpeg'
			im = PImage.open(pdir+'/edit/'+filename).save(pdir+'/'+fname, "JPEG")
		    else:
			if ext != "png": 
			    im = PImage.open(pdir+'/edit/'+filename).save(pdir+'/'+fname+'.png', "PNG")
			    fname = fname+'.png'
			else: 
			    im = PImage.open(pdir+'/edit/'+filename).save(pdir+'/'+fname, "PNG")
			content_t = 'image/png'
		else:
		    execute('cp '+pdir+'/edit/'+filename+' '+pdir+'/'+fname)
		    content_t = saved_image.content_type
		im = PImage.open(pdir+'/'+fname)
		new_image = Image()
		new_image.user = request.user
		new_image.data = (pdir+'/'+fname).replace(MEDIA_ROOT,'')
		new_image.content_type = content_t
		new_image.width, new_image.height = im.size
		if new_image.width > 600:
		    new_image.status = 0
		else:
		    new_image.status = 1
		new_image.save()
		return
		
	    im = PImage.open(pdir+'/edit/'+filename)
            if action == "resize":            
                width = request.GET.get("width")
                height = request.GET.get("height")
                if width and height:
                    img = im.resize((int(width),int(height)))
		    #images.resize(saved_image.data, int(width), int(height), saved_image.output_encoding)
            elif action == "rotate":
                degrees = request.GET.get("degrees")
                if degrees:
                    img = im.rotate(int(degrees))
		    #images.rotate(saved_image.data, int(degrees), saved_image.output_encoding)
            elif action == "crop":
                left_x = request.GET.get("left_x")
                top_y = request.GET.get("top_y")
                right_x = request.GET.get("right_x")
                bottom_y = request.GET.get("bottom_y")
                if left_x and top_y and right_x and bottom_y:
		    box = (int(left_x), int(top_y), int(right_x), int(bottom_y))
                    img = im.crop(box)
		    #images.crop(saved_image.data, float(left_x), float(top_y), float(right_x), float(bottom_y), saved_image.output_encoding)
            if img:
                # save new settings
#                output_encoding = saved_image.output_encoding
		if (saved_image.content_type=='image/jpeg'):
		    img.save(pdir+'/edit/'+filename,"JPEG")
		else:
		    img.save(pdir+'/edit/'+filename,"PNG")
	