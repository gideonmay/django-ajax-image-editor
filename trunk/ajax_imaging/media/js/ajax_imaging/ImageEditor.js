/*
ImageEditor.js
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

ImageEditor = {
	w: 0,
	h: 0,
	startX: 0,
	startY: 0,
	mouseIsDown: false,
	loadingTextInterval: 0,
    editorImage: null,
	loaderImage: null,
    cropRegion: document.createElement("div"),
	validDimension: /^\d{1,4}$/
};
UrlPrefix = window.location;
ImageEditor.processImage = function(args){
	if (ImageEditor.cropRegion){
		ImageEditor.cropRegion.style.display = "none";
		ImageEditor.hideCropSize();
	}
	ImageEditor.showLoading();
	var request = (window.XMLHttpRequest) ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
	request.open("GET", UrlPrefix+"processImage/?"+args, true);
	request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	request.onreadystatechange = function(){
		if (request.readyState == 4){
            ImageEditor.loadImage();
		}
	};
	request.send((args) ? args : null);
};
ImageEditor.loadImage = function(){
	ImageEditor.loaderImage.setAttribute("src", UrlPrefix+"getImage/?t=" + (new Date).getTime());
};
ImageEditor.displayImage = function(){

    clearInterval(ImageEditor.loadingTextInterval);
    
    ImageEditor.w = ImageEditor.loaderImage.offsetWidth;
    ImageEditor.h = ImageEditor.loaderImage.offsetHeight;
    
    var editorImage = ImageEditor.editorImage;
	editorImage.innerHTML = "";
	editorImage.style.width = ImageEditor.w + "px";
	editorImage.style.height = ImageEditor.h + "px";
	editorImage.style.backgroundImage = "url(" + ImageEditor.loaderImage.getAttribute('src') + ")";

	document.getElementById("txt-width").value = ImageEditor.w;
	document.getElementById("txt-height").value = ImageEditor.h;
};
ImageEditor.showLoading = function(){
    ImageEditor.editorImage.style.backgroundImage = "none";
    ImageEditor.editorImage.innerHTML =
		'<div id="loading-text">Loading Image<span id="ellipsis">...</span></div>';
	ImageEditor.loadingTextInterval = setInterval(function(){
		if (document.getElementById("ellipsis")){
			var dots = document.getElementById("ellipsis").innerHTML;
			document.getElementById("ellipsis").innerHTML = (dots != "...") ? dots += "." : "";
		}
	}, 500);
};
ImageEditor.txtWidthKeyup = function(){
	var w = document.getElementById("txt-width").value;
	if (ImageEditor.validDimension.test(w)){
		document.getElementById("txt-width").value = parseInt(w);
		document.getElementById("txt-height").value = parseInt((w * ImageEditor.h)/ImageEditor.w);
	}else if (w == ""){
		document.getElementById("txt-height").value = "";	
	}else{
		document.getElementById("txt-width").value = w.replace(/[^0-9]/g, "");
	}
};
ImageEditor.txtHeightKeyup = function(){
	var h = document.getElementById("txt-height").value;
	if (ImageEditor.validDimension.test(h)){
		document.getElementById("txt-height").value = parseInt(h);
		document.getElementById("txt-width").value = parseInt((h * ImageEditor.w)/ImageEditor.h);	
	}else if (h == ""){
		document.getElementById("txt-width").value = "";
	}else{
		document.getElementById("txt-height").value = h.replace(/[^0-9]/g, "");	
	}
};
ImageEditor.txtBlur = function(){
	var w = document.getElementById("txt-width").value;
	var h = document.getElementById("txt-height").value;
	if (!ImageEditor.validDimension.test(w) || !ImageEditor.validDimension.test(h)){
		document.getElementById("txt-width").value = ImageEditor.w;
		document.getElementById("txt-height").value = ImageEditor.h;	
	}
}
ImageEditor.resize = function(){
	var width = document.getElementById("txt-width").value;
	var height = document.getElementById("txt-height").value;
	
    if (!ImageEditor.validDimension.test(width) || !ImageEditor.validDimension.test(height)){
		alert("The image dimensions are not valid.");
		document.getElementById("txt-width").value = ImageEditor.w;
		document.getElementById("txt-height").value = ImageEditor.h;
		return;
	}
    if (width > 2000 || height > 2000){
		alert("Width and/or height cannot exceed 2000 pixels.");
		document.getElementById("txt-width").value = ImageEditor.w;
		document.getElementById("txt-height").value = ImageEditor.h;
		return;
	}
	ImageEditor.processImage("action=resize&width=" + width + "&height=" + height);
};
ImageEditor.rotate = function(degrees){
	ImageEditor.processImage("action=rotate&degrees=" + degrees);
};
ImageEditor.viewActive = function(){
        ImageEditor.processImage("action=view_active");
};
ImageEditor.viewOriginal = function(){
        ImageEditor.processImage("action=view_original");
};
ImageEditor.save = function(){
        ImageEditor.processImage("action=save");
};
ImageEditor.save_as = function(){
	ImageEditor.processImage("action=save_as&fname="+document.getElementById("txt-fname").value)
};
ImageEditor.undo = function(){
   ImageEditor.processImage("action=undo");
};
ImageEditor.crop = function(){
	if (typeof ImageEditor == "undefined") { return; }
	if (ImageEditor.cropRegion.style.display == "none"){
		alert("You must select an area to crop before using this feature.");
		return;
	}
	var left = parseInt(ImageEditor.cropRegion.style.left) - PageInfo.getElementLeft(ImageEditor.editorImage);
	var top = parseInt(ImageEditor.cropRegion.style.top) - PageInfo.getElementTop(ImageEditor.editorImage);
	var width = parseInt(ImageEditor.cropRegion.style.width);
	var height = parseInt(ImageEditor.cropRegion.style.height);
    
    left_x = left 
    // ImageEditor.w;
    top_y = top 
    // ImageEditor.h;
    right_x = (left + width) 
    // ImageEditor.w;
    bottom_y = (top + height) 
    // ImageEditor.h;
    
    ImageEditor.processImage("action=crop&left_x=" + left_x + "&top_y=" + top_y + "&right_x=" + right_x + "&bottom_y=" + bottom_y);
};
ImageEditor.startCrop = function(){
	if (typeof ImageEditor == "undefined") { return; }
    
    var cropRegionStyle = ImageEditor.cropRegion.style;
    cropRegionStyle.left = PageInfo.getMouseX() + "px";
    cropRegionStyle.top = PageInfo.getMouseY() + "px";
    cropRegionStyle.width = "1px";
    cropRegionStyle.height = "1px";
    cropRegionStyle.display = "block";
	
    ImageEditor.startX = PageInfo.getMouseX();
	ImageEditor.startY = PageInfo.getMouseY();
};
ImageEditor.dragCrop = function(){
	if (typeof ImageEditor == "undefined") { return; }
	if (!ImageEditor.mouseIsDown) { return; }

	// mouse is to the right of starting point
	if (PageInfo.getMouseX() - ImageEditor.startX > 0) {
		ImageEditor.cropRegion.style.width = PageInfo.getMouseX() - ImageEditor.startX + "px";
	} else{ // mouse is to the left of starting point
		ImageEditor.cropRegion.style.left = PageInfo.getMouseX() + "px";
		ImageEditor.cropRegion.style.width = ImageEditor.startX - PageInfo.getMouseX() + "px";
	}
	// mouse is below the starting point
	if (PageInfo.getMouseY() - ImageEditor.startY > 0) {
		ImageEditor.cropRegion.style.height = PageInfo.getMouseY() - ImageEditor.startY + "px";
	} else { // mouse is above the starting point
		ImageEditor.cropRegion.style.top = PageInfo.getMouseY() + "px";
		ImageEditor.cropRegion.style.height = ImageEditor.startY - PageInfo.getMouseY() + "px";
	}
	ImageEditor.showCropSize(parseInt(ImageEditor.cropRegion.style.width), parseInt(ImageEditor.cropRegion.style.height));
};
ImageEditor.slideCrop = function(e){
	if (ImageEditor.cropRegion.style.display == "none") { return; }
	e = e || event;
	var code = (e.keyCode) ? e.keyCode : (e.which) ? e.which : null;
	if (!code) { return };
	switch (code){
		case 37: //left
			if(PageInfo.getElementLeft(ImageEditor.cropRegion) > PageInfo.getElementLeft(ImageEditor.editorImage)){
				ImageEditor.cropRegion.style.left = PageInfo.getElementLeft(ImageEditor.cropRegion) - 1 + "px";
			}
			break;
		case 38: //up
			if(PageInfo.getElementTop(ImageEditor.cropRegion) > PageInfo.getElementTop(ImageEditor.editorImage)){
				ImageEditor.cropRegion.style.top = PageInfo.getElementTop(ImageEditor.cropRegion) - 1 + "px";
			}		
			break;
		case 39: //right
			if (PageInfo.getElementLeft(ImageEditor.cropRegion) + PageInfo.getElementWidth(ImageEditor.cropRegion) < PageInfo.getElementLeft(ImageEditor.editorImage) + PageInfo.getElementWidth(ImageEditor.editorImage)){
				ImageEditor.cropRegion.style.left = PageInfo.getElementLeft(ImageEditor.cropRegion) + 1 + "px";
			}
			break;
		case 40: //down
			if (PageInfo.getElementTop(ImageEditor.cropRegion) + PageInfo.getElementHeight(ImageEditor.cropRegion) < PageInfo.getElementTop(ImageEditor.editorImage) + PageInfo.getElementHeight(ImageEditor.editorImage)){
				ImageEditor.cropRegion.style.top = PageInfo.getElementTop(ImageEditor.cropRegion) + 1 + "px";
			}		
			break;
	}
};
ImageEditor.showCropSize = function(w, h){
	document.getElementById("crop-size").innerHTML = w + " by " + h + " (use arrow keys to slide)";
};
ImageEditor.hideCropSize = function(){
	document.getElementById("crop-size").innerHTML = "";
};
ImageEditor.addEvent = function(obj, evt, func){
	if (window.addEventListener){
		obj.addEventListener(evt, func, false);
	}else if (window.attachEvent){
		obj.attachEvent("on" + evt, func);
	}
};
ImageEditor.init = function(){

    ImageEditor.editorImage = document.getElementById("image");

    ImageEditor.loaderImage = document.getElementById("loader-image");
	ImageEditor.loaderImage.onload = function(){ ImageEditor.displayImage(); };

	ImageEditor.loadImage();
	
    ImageEditor.cropRegion.className = "cropRegion";
	var bodyNode = document.getElementsByTagName("body").item(0);
	bodyNode.appendChild(ImageEditor.cropRegion);
	
	ImageEditor.addEvent(document, "mousedown", function(){ ImageEditor.mouseIsDown = true; });
	ImageEditor.addEvent(document, "mouseup", function(){ ImageEditor.mouseIsDown = false; });
	ImageEditor.addEvent(ImageEditor.editorImage, "mouseover", function(){ ImageEditor.editorImage.style.cursor = "crosshair"; });
	ImageEditor.addEvent(ImageEditor.editorImage, "mousedown", ImageEditor.startCrop);
	ImageEditor.addEvent(ImageEditor.editorImage, "mousemove", ImageEditor.dragCrop);
	ImageEditor.addEvent(ImageEditor.cropRegion, "mousedown", ImageEditor.startCrop);
	ImageEditor.addEvent(ImageEditor.cropRegion, "mousemove", ImageEditor.dragCrop);
	ImageEditor.addEvent(document, "dblclick", function() { ImageEditor.cropRegion.style.display = "none"; ImageEditor.hideCropSize(); });
	ImageEditor.addEvent(document, "keydown", ImageEditor.slideCrop);
	ImageEditor.addEvent(document.getElementById("txt-width"), "keyup", ImageEditor.txtWidthKeyup);
	ImageEditor.addEvent(document.getElementById("txt-width"), "blur", ImageEditor.txtBlur);
	ImageEditor.addEvent(document.getElementById("txt-height"), "keyup", ImageEditor.txtHeightKeyup);
	ImageEditor.addEvent(document.getElementById("txt-height"), "blur", ImageEditor.txtBlur);
};