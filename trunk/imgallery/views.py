'''
Created on 15.08.2009

@author: german
'''
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.urlresolvers import reverse
from imgallery.models import Folder, ArticleFolder
from imgallery.forms import FolderForm, ArticleFolderForm
from django.utils import simplejson
from sorl.thumbnail.main import DjangoThumbnail
from ajax_imaging.forms import ImageForm, ImageEditForm
from ajax_imaging.models import Image
import os
import logging

@login_required
def create_gallery(request, type='photo', news_id = None, template_name='imgallery/create-gallery.html'):
    if type == 'photo':
        folder = Folder(user=request.user, type=1)
        form_class = FolderForm
    else:
        form_class = ArticleFolderForm
        folder = ArticleFolder(user=request.user, type=2)
        if news_id is not None:
            try:
                news = News.objects.get(pk=news_id, author=request.user.profile.author)
                folder.news = news
            except:
                return Http404()

    if request.method == "POST":
        form = form_class(request.POST, instance = folder)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('my_image_folders'))
    else:
        form = form_class(instance=folder)
    c = RequestContext(request, {'form': form})
    return render_to_response(template_name, c)

def get_images_of_injson(request, id):
    user = request.user
    data = {}
    try:
        folder = Folder.objects.all_galleries(user).get(pk=id)
        list =  folder.images.all()
        if list.count() == 0:
            data = {'error': 'no images'}
        else:
            data.update({"ids": [x.id for x in list]})
            data.update({"names": [os.path.basename(x.data.name) for x in list]})
            data.update({"sizes": [int(x.data.size/1024.0) for x in list]})
            data.update({"thumb_list" : [DjangoThumbnail(x.data,(96,96),["crop","upscale"]).relative_url for x in list]})
            data.update({"orig_list" : [x.data.url for x in list]})
    except Folder.DoesNotExist:
        data["error"] = "No such folder"
    return data

def move_image(request, image_id, from_id, to_id):
    try:
        try:
            fromf = Folder.objects.all_galleries(user=request.user).get(images__pk=image_id, pk=from_id)
            tof = Folder.objects.all_galleries(user=request.user).get(pk=to_id)
        except Folder.DoesNotExist:
            return {'error': 'no folder'}
    except:
        return {'error': 'error in query'}
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        return {'error': 'image does not exist'}
    try:
        fromf.images.remove(image)
        tof.images.add(image)
        fromf.save()
        tof.save()
    except:
        return {'error': 'error in moving'}
    return {'success': 'all right'}

def delete_image(request, folder_id, image_id):
    try:
        folder = Folder.objects.all_galleries(user=request.user).get(pk=folder_id)
        try:
            folder.images.get(pk=image_id).delete()
        except:
            return {'error': 'error while deleting from folder'}
    except Folder.DoesNotExist:
        return {'error': 'no such foler'}
    return {'success': 'all right'}

def delete_folder(request, folder_id):
    try:
        folder = Folder.objects.all_galleries(user=request.user).get(pk=folder_id)
        folder.images.all().delete()
        folder.delete()
    except Folder.DoesNotExist:
        return {'error': 'no such foler'}
    return {'success': 'all right'}

@login_required
def my_folder_list(request, template_name='imgallery/folder-list-v2.html'):
    user = request.user
    if request.is_ajax():
        action = request.POST.get("action", "imlist")
        if action == "imlist":
            id = request.POST.get("object_id")
            data = get_images_of_injson(request, id)
        elif action == "move":
            image_id, to_id, from_id = request.POST.get("image_id"), request.POST.get("folder_id"), request.POST.get("cfolder_id")
            data = move_image(request, image_id, from_id, to_id)
        elif action == "delete-image":
            folder_id = request.POST.get("folder_id")
            image_id = request.POST.get("image_id")
            data = delete_image(request, folder_id, image_id)
        elif action == "delete-folder":
            folder_id = request.POST.get("folder_id")
            data = delete_folder(request, folder_id)
        json = simplejson.dumps(data)
        return HttpResponse(json, mimetype="application/json")
    default = Folder.objects.default(user)
    list = Folder.objects.all_galleries(user).order_by("-pk")
    upform = ImageForm()
    editform = ImageEditForm()
    c = RequestContext(request, {'object_list': list, 'form': upform, 'editform': editform})
    return render_to_response(template_name, c)

def photo_gallery_details(request, id=None, template_name='ajax_imaging/gallery-details.html'):
    if not id:
        return Http404()
    
    try:
        folder = Folder.objects.get(pk=id)
    except Folder.DoesNotExist:
        return Http404()
    
    if folder.public or (folder.user == request.user and request.user.is_authenticated()):
        c = RequestContext(request, {'folder': folder})
        return render_to_response(template_name, c)
    else:
        return Http404()
