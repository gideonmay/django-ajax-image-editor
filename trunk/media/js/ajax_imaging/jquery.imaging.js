/*
jquery.imaging.js
Copyright (C) 2008 Peter Frueh (http://www.ajaxprogrammer.com/)

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
*/

function deleteImage(lel,id){
	$.ajax({
        type: "POST",
        dataType: "json",
        url: $(lel).attr("href"),
        success: function(json){
        	if (json.success){
				$("#gallery").find("li[id='id-"+id+"']").remove('');
				$("#gallery").find("li:first").find("img").click();
				return false;
            }
        }
    });
    return false;
}

function update_gallery(json){
	var t = '<li id="id-'+json.new_id+'" class="ui-widget-content ui-corner-tr">'+
    '<h5 class="ui-widget-header">'+json.new_id+'</h5>' +
    '<img onClick="ImageEditor.changeImage('+json.new_id+');" style="margin:0px;padding:0px;" src="'+$("li[id='id-"+id+"']").find("img").attr("src")+'" alt="'+save_as+'" />' +
    '<a onClick="deleteImage(this,'+json.new_id+');return false;" href="'+ImageEditor.UrlPrefix+json.new_id+'/delete/'+'" title="Delete this image" class="ui-icon ui-icon-trash">Delete image</a>' +
    '<div class="ui-helper-clearfix"></div>' +	                                      
    '</li>';
	$("#gallery").append(t);
}


ImageEditor = {
	w: 0,
	h: 0,
	ias_api: null, 
	loadingTextInterval: 0,
    editorImage: null,
	loaderImage: null,
	changes: false,
	show: true, 
	selection: {x1:0,x2:0,y1:0,y2:0},
    cropRegion: document.createElement("div"),
	validDimension: /^\d{1,4}$/,
	UrlPrefix: '/imaging/',
	dw: 0,
	dh: 0,
	maxW: 700
};
ImageEditor.do_show = function(){
	ImageEditor.show = true;
	if (ImageEditor.ias_api != null){
		ImageEditor.ias_api.setOptions({show:true});
		ImageEditor.ias_api.update();
	}
}
ImageEditor.do_hide = function(){
	ImageEditor.show = false;
	if (ImageEditor.ias_api != null){
		ImageEditor.ias_api.setOptions({hide:true});
		ImageEditor.ias_api.update();
	}

}
ImageEditor.processImage = function(/*args*/){
	ImageEditor.showLoading();
	var id = $("form#editform").find("input[name='image']").val();
	var action = $("form#editform").find("input[name='action']").val();
	var save_as = $("form#editform").find("input[name='save_as']").val();
	$.ajax({
        type: "POST",
        dataType: "json",
        url: ImageEditor.UrlPrefix+id+'/processImage/',
        data: $("#editform").serialize(),
        success: function(json){
        	if (json.success){
	        	if (action == "save_as"||action=="save"){
	        		ImageEditor.changes = false;
	        	}else{
	        		ImageEditor.changes = true; 
	        	}
               ImageEditor.loadImage();
				if (action == "save_as"){
               		if (json.new_id){
               			update_gallery(json);
               		}
				}              
            }
        }
    });
};
ImageEditor.loadImage = function(){
	ImageEditor.showLoading();
	id = $("form#editform").find("input[name='image']").val();
	$(ImageEditor.loaderImage).attr("src", ImageEditor.UrlPrefix+id+"/getImage/?t=" + (new Date).getTime());
};
ImageEditor.displayImage = function(){
	ImageEditor.showLoaded();
    clearInterval(ImageEditor.loadingTextInterval);
    ImageEditor.w = $(ImageEditor.loaderImage).attr("width");
    ImageEditor.h = $(ImageEditor.loaderImage).attr("height");
    ImageEditor.dw = (ImageEditor.w > ImageEditor.maxW) ? ImageEditor.maxW : ImageEditor.w;
    ImageEditor.dh = Math.round(ImageEditor.dw*ImageEditor.h/ImageEditor.w);
    var editorImage = ImageEditor.editorImage;
	$(editorImage).attr("width",ImageEditor.dw); //= ImageEditor.w + "px";
	$(editorImage).attr("height",ImageEditor.dh);// = ImageEditor.h + "px";
	$(editorImage).attr("src",$(ImageEditor.loaderImage).attr("src"));
	$("#txt-width").val(ImageEditor.w);
	$("#txt-height").val(ImageEditor.h);
};
ImageEditor.showLoaded = function(){
	$("#status").html('<div id="loading-text">Картинка загружена</div>');
};
ImageEditor.showLoading = function(){
    $("#status").html('<div id="loading-text">Загрузка картинки<span id="ellipsis">...</span></div>');
	ImageEditor.loadingTextInterval = setInterval(function(){
		if ($("#ellipsis")){
			var dots = $("#ellipsis").html();
			$("#ellipsis").html((dots != "...") ? dots += "." : "");
		}
	}, 500);
};
ImageEditor.resize = function(){
	var width = $("#txt-width").val();
	var height = $("#txt-height").val();
	
    if (!ImageEditor.validDimension.test(width) || !ImageEditor.validDimension.test(height)){
		alert("The image dimensions are not valid.");
		$("#txt-width").val(ImageEditor.w);
		$("#txt-height").val(ImageEditor.h);
		return;
	}
    if (width > 2000 || height > 2000){
		alert("Width and/or height cannot exceed 2000 pixels.");
		$("#txt-width").val(ImageEditor.w);
		$("#txt-height").val(ImageEditor.h);
		return;
	}
    $("form#editform").find("input[name='resize_height']").val($("#txt-height").val());
    $("form#editform").find("input[name='resize_width']").val($("#txt-width").val());
    $("form#editform").find("input[name='action']").val('resize');
	
	ImageEditor.processImage();
};
ImageEditor.rotate = function(degrees){
	$("form#editform").find("input[name='degrees']").val(degrees);
	$("form#editform").find("input[name='action']").val('rotate');
	ImageEditor.processImage();
};
ImageEditor.viewActive = function(){
	$("form#editform").find("input[name='action']").val('view_active');
    ImageEditor.processImage();
};
ImageEditor.viewOriginal = function(){
	$("input[name='action']").val('view_original');
	ImageEditor.processImage();
};
ImageEditor.save = function(){
	$("form#editform").find("input[name='action']").val('save');
	ImageEditor.processImage();
};
ImageEditor.save_as = function(){
	$("form#editform").find("input[name='action']").val('save_as');
	$("form#editform").find("input[name='save_as']").val(prompt("New filename?"));
	ImageEditor.processImage();
};
ImageEditor.undo = function(){
	$("form#editform").find("input[name='action']").val('undo');
	ImageEditor.processImage();
};
ImageEditor.crop = function(){
	if (ImageEditor.ias_api != null){
		$("form#editform").find("input[name='action']").val('crop');
		ImageEditor.updateCropValues(null, ImageEditor.selection);
	    ImageEditor.processImage();
	    return true;
    }else return false;
};
ImageEditor.addEvent = function(obj, evt, func){
	if (window.addEventListener){
		obj.addEventListener(evt, func, false);
	}else if (window.attachEvent){
		obj.attachEvent("on" + evt, func);
	}
};

function previewAvatar(img, selection) {
}
ImageEditor.updateCropValues = function(img, selection){
	ImageEditor.selection = selection;
	$("form#editform").find("input[name='left']").val(Math.round(selection.x1));
	$("form#editform").find("input[name='top']").val(Math.round(selection.y1));
	$("form#editform").find("input[name='right']").val(Math.round(selection.x2));
	$("form#editform").find("input[name='bottom']").val(Math.round(selection.y2));
	$("form#editform").find("input[name='display_width']").val(ImageEditor.dw);
	$("form#editform").find("input[name='display_height']").val(ImageEditor.dh);
};
ImageEditor.changeImage = function(id){
	$("form#editform").find("input[name='image']").val(id);
	$("#image-title").html('Image name: '+$("#gallery li[id='id-"+id+"'] img").attr("alt"));
	ImageEditor.loadImage();
};
ImageEditor.init = function(){
	var self = this; 
    self.editorImage = $("#image-editor img#image");
    self.loaderImage = $("#image-editor #loader-image");
	$(ImageEditor.loaderImage).load(function(){ ImageEditor.displayImage(); });
	ImageEditor.loadImage();
	$("a[name='b_original']").click(ImageEditor.viewOriginal);
	$("a[name='b_save']").click(ImageEditor.save);
	$("a[name='b_save_as']").click(ImageEditor.save_as);
	$("a[name='b_undo']").click(ImageEditor.undo);
	$("a[name='b_resize']").click(ImageEditor.resize);
	$("a[name='b_cw']").click(function(){ImageEditor.rotate(270)});
	$("a[name='b_ccw']").click(function(){ImageEditor.rotate(90)});
	$("a[name='b_crop']").click(ImageEditor.crop);
	$(ImageEditor.editorImage).load(function(){
		var selection = ImageEditor.selection;
		var w = ImageEditor.dw/2;
		var h = ImageEditor.dh/2;
		selection.x1 = w/2;
		selection.y1 = h/2;
		selection.x2 = ImageEditor.dw - w/2;
		selection.y2 = ImageEditor.dh - h/2;
		ImageEditor.selection = selection;
		ImageEditor.updateCropValues(null, selection);
		if (ImageEditor.ias_api != null){
			ImageEditor.ias_api.setOptions({show: ImageEditor.show});
			ImageEditor.ias_api.setSelection(selection.x1, selection.y1, selection.x2,  selection.y2);
			ImageEditor.ias_api.update();	
		}else{
			self.ias_api = $(ImageEditor.editorImage).imgAreaSelect({
					handles: 'corners',
					instance: true,
					minHeight: "16",
					minWidth: "16",
					show: ImageEditor.show, 
					x1: selection.x1,
					x2: selection.x2,
					y1: selection.y1,
					y2: selection.y2,
					onSelectEnd: ImageEditor.updateCropValues
			});
		}
	});
};

