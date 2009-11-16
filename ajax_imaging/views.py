from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.core.files import File
from ajax_imaging.models import Image
from ajax_imaging.forms import ImageForm, ImageEditForm
from imgallery.models import *
from django.conf import settings
import logging
try:
    from PIL import Image as PImage
except ImportError:
    import Image as PImage
import os
from subprocess import *
from ajax_imaging.getimageinfo import getImageInfo
from cStringIO import StringIO
from django.core.files.base import ContentFile
from django.utils import simplejson
import mimetypes

if hasattr(settings, 'MAX_IMAGE_WIDTH'):
    MAX_IMAGE_WIDTH = settings.MAX_IMAGE_WIDTH
else:
    MAX_IMAGE_WIDTH = 600

def z_copy(from_d, to_d):
    f = open(from_d,"rb")
    t = open(to_d,"wb")
    t.write(f.read())
    f.close()
    t.close()
    """
    if os.name == "posix":
        execute('cp %(from)s %(to)s' % {'from':from_d,'to':to_d});
    elif os.name == "nt":
        execute('copy %(from)s %(to)s' % {'from':from_d,'to':to_d});
    """

def z_swap(from_d, to_d):
    f = open(to_d,"rb")
    s = StringIO(f.read())
    f.close()
    z_copy(from_d,to_d)
    f = open(from_d,"wb")
    s.seek(0)
    f.write(s.read())
    f.close()
    """
    if os.name == "posix":
        execute('mv %(from)s %(to)s' % {'from':from_d,'to':from_d+'_'});
        execute('mv %(from)s %(to)s' % {'from':to_d,'to':from_d});
        execute('mv %(from)s %(to)s' % {'from':from_d+'_','to':to_d});
    elif os.name == "nt":
        execute('move %(from)s %(to)s' % {'from':from_d,'to':from_d+'_'});
        execute('move %(from)s %(to)s' % {'from':to_d,'to':from_d});
        execute('move %(from)s %(to)s' % {'from':from_d+'_','to':to_d});
    """

@login_required
def image_list(request):
    if request.POST:
    	delimg = request.POST.getlist('delimg[]')
    	Image.objects.filter(id__in=delimg).delete()
    	return HttpResponseRedirect(reverse('my_image_archive'))

    list = Image.objects.filter(user=request.user)
    f = ImageForm()
    ef = ImageEditForm(initial={'image':1})
    c = RequestContext(request, {'list' : list, 'form': f, 'editform': ef})
    return render_to_response('ajax_imaging/list.html', c)

@login_required
def main(request,id=1):
    c = RequestContext(request)
    """
    if os.path.exists(settings.MEDIA_ROOT+'uploads/'+request.user.username+'/image_archive/undo/'):
    	execute("rm "+settings.MEDIA_ROOT+"uploads/"+request.user.username+"/image_archive/undo/*")
    if os.path.exists(settings.MEDIA_ROOT+'uploads/'+request.user.username+'/image_archive/edit/'):
    	execute("rm "+settings.MEDIA_ROOT+"uploads/"+request.user.username+"/image_archive/edit/*")
    """
    return render_to_response('ajax_imaging/index.html',c)

@login_required
def upload(request):
    if request.POST or request.FILES:
        n = int(request.POST.get("file_count",1))
        logging.info(n)
        logging.info(request.FILES["data"])
        fid = int(request.POST.get("folder",0))
        if fid:
            try:
                folder = Folder.objects.all_galleries(user=request.user).get(pk=fid)
            except Folder.DoesNotExist:
                folder = Folder.objects.default(user=request.user)
        else:
            folder = Folder.objects.default(user=request.user)
        if n > 1:
            imgs = request.FILES.getlist('data')
        else:
            img = request.FILES['data']
            imgs = [img]
        exts = set(['.jpg','.png','.zip'])
        g = 0;
        for img in imgs:
            #if exts & set(mimetypes.guess_all_extensions(img.content_type)):
                g = g + 1
                if g > 3:
                    break;
                im = PImage.open(ContentFile(img.read()))
                content_type = img.content_type
                width, height = im.size
                if width > MAX_IMAGE_WIDTH:
                    im.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_WIDTH*height/width), PImage.ANTIALIAS)
                    im.convert("RGB")
                    f = StringIO()
                    im.save(f, "JPEG")
                    width, height = MAX_IMAGE_WIDTH, MAX_IMAGE_WIDTH*height/width
                else:
                    f = img
                    
                if not img or not content_type:
                    continue
        
                image = Image(user=request.user, width =width, height=height, content_type=content_type)
                """
                image.user = request.user
                if content_type == "image/jpeg":
                    image.content_type = "image/jpeg"
                else:
                    image.content_type = "image/png"
                image.width = width
                image.height = height
                """
                if width>600:
                    image.status = 0
                else:
                    image.status = 1
        
                f.seek(0)
                image.data.save(img.name, ContentFile(f.read()))
                image.save()

                folder.images.add(image)
        folder.save()
                
    if request.POST.get('next','') != '':
        return HttpResponseRedirect(request.POST['next'])
    else:
        return HttpResponseRedirect(reverse('my_image_archive'))

@login_required
def delete_image(request, id=1):
    data = {'success': 'Deleted successfully'}
    try:
        im = Image.objects.get(user=request.user,pk=id)
        im.data.delete()
        im.delete()
    except Image.DoesNotExist:
        data = {'errors': 'No such image'}
    if request.is_ajax():
        json = simplejson.dumps(data)
        return HttpResponse(json, mimetype="application/json")
    else:
        return HttpResponseRedirect(reverse("my_image_archive"))

@login_required
def get_image(request,id=1):
    if request.method=="GET":
    	try:
    	    image = Image.objects.get(pk=id)
    	    path = image.data.path
    	    pdir = os.path.dirname(path)
    	    filename = os.path.basename(path)
    	    if not os.path.exists(pdir+'/edit/'):
                os.mkdir(pdir+'/edit/')

            if not os.path.exists(pdir+'/undo/'):
                os.mkdir(pdir+'/undo/')
            if not os.path.exists(pdir+'/edit/'+filename):
                z_copy(path, pdir+'/edit/'+filename)

            if not os.path.exists(pdir+'/undo/'+filename):
                z_copy(path, pdir+'/undo/'+filename)
            for root, dirs, files in os.walk(pdir+'/edit/'):
                for name in files:
                    if name != filename:
                        os.remove(os.path.join(root,name))

            for root, dirs, files in os.walk(pdir+'/undo/'):
                for name in files:
                    if name != filename:
                        os.remove(os.path.join(root,name))
    	    f = open(pdir+'/edit/'+filename,"rb")
    	    response = HttpResponse(f.read(), mimetype=image.content_type, content_type=image.content_type)
    	    f.close()
    	    return response
    	except:
    	    return None

def execute(cmd):
    return os.system(cmd)
    #p = Popen(cmd, shell=True, stdout=PIPE)
    #p.wait()
    #return (p.stdout, p.returncode)



@login_required
def process_image(request,id=1):
    if request.method=="POST":
        data = {'success':'all done'}
        try:
            imo = Image.objects.get(pk=id)
            path = imo.data.path
            pdir = os.path.dirname(path)
            filename = os.path.basename(path)
            edit_d = pdir+'/edit/'
            undo_d = pdir+'/undo/'
            active_d = pdir+'/active/'
            editform = ImageEditForm(request.POST)
            if editform.is_valid():
                cd = editform.cleaned_data
                action = cd.get("action")
                if action in ['undo','view_original','view_avtive','save','save_as']:
                    if action == "undo":
                        z_swap(edit_d+filename, undo_d+filename)
                    elif action == "view_original":
                        z_copy(path, edit_d+filename)
                    elif action == "view_active":
                        z_copy(active_d+filename,edit_d+filename)
                    elif action == "save":
                        z_copy(edit_d+filename, path)
                        im = PImage.open(path)
                        imo.width, imo.height = im.size
                        if imo.width > 600:
                            imo.status = 0
                        else:
                            imo.status = 1
                        imo.save()
                    elif action == "save_as":
                        fname = cd.get("save_as")
                        fname = os.path.basename(fname)
                        k = fname.split(os.extsep)
                        iext = filename.split(os.extsep)[-1].lower()
                        ext = k[-1].lower()
                        #f = StringIO()
                        im = PImage.open(edit_d+filename)
                        im.convert("RGB")
                        if (ext != iext):
                            if (ext == "jpg" or ext == "jpeg"):
                                content_t = 'image/jpeg'
                                im = im.save(pdir+'/'+fname, "JPEG")
                            else:
                                if ext != "png":
                                    fname = fname+'.png'
                                    im = im.save(pdir+'/'+fname, "PNG")
                                else:
                                    im = im.save(pdir+'/'+fname, "PNG")
                            content_t = 'image/png'
                        else:
                            im = im.save(pdir+'/'+fname)
                            #z_copy(edit_d+filename, pdir+'/'+fname)
                            content_t = imo.content_type
                        im = PImage.open(pdir+'/'+fname)
                        #f.seek(0)
                        new_image = Image()
                        new_image.user = request.user
                        new_image.data = (pdir+'/'+fname).replace(settings.MEDIA_ROOT,'')
                        #.save(fname, ContentFile(f.read()));
                        new_image.content_type = content_t
                        new_image.width, new_image.height = im.size
                        if new_image.width > 600:
                            new_image.status = 0
                        else:
                            new_image.status = 1
                        new_image.save()
                        folder = Folder.objects.default(user=request.user)
                        folder.images.add(new_image);
                        folder.save();
                        data.update({'new_id': new_image.id})
                else:
                    z_copy(edit_d+filename, undo_d+filename)
                    im = PImage.open(edit_d+filename)
                    if action == "resize":
                        img = im.resize((int(cd.get("resize_width")),int(cd.get("resize_height"))))
                    elif action == "rotate":
                        img = im.rotate(int(cd.get("degrees")))
                    elif action == "crop":
                        dw = cd.get("display_width")
                        dh = cd.get("display_height")
                        cf = 1.0
                        width, height = im.size
                        if dw != width and dw:
                            cf = width/float(dw);
                        left = int(int(cd.get("left"))*cf)
                        top = int(int(cd.get("top"))*cf)
                        right = int(int(cd.get("right"))*cf)
                        bottom = int(int(cd.get("bottom"))*cf)

                        box = (left, top, right, bottom)
                        img = im.crop(box)
                    if img:
                        if (imo.content_type=='image/jpeg'):
                            img.save(edit_d+filename,"JPEG")
                        else:
                            img.save(edit_d+filename,"PNG")
                #z_copy(imo, 'edit','undo')
            else:
                data = {'errors': editform.errors}
        except Image.DoesNotExist:
            data = {'errors':['no such image']}
    else:
        data = {'errors':['invalid request']}
    json = simplejson.dumps(data)
    return HttpResponse(json, mimetype='application/json')