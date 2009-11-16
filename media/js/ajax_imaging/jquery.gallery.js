var gallery = {
		api: null ,
		eapi: null
}
	gallery.changeImage = function(id){
		$("form#editform").find("input[name='image']").val(id);
	}
	gallery.addFile = function (){
		var form = $("form.add-image-form");
		var counter = $(form).find("input[name='file_count']");
		var item = $(form).find("div#input:has(input[name='data']):last");
		var clone = item.clone();
		
		var n = parseInt($(counter).val());
		$(clone).find("input[name='data']").val('');
		$(item).after(clone);
		$(counter).val(n+1);
	}
	gallery.deleteFolder = function(o, id){
		if (confirm("Удалить галерею?\nВсе фотографии в галереи будут удалены!")){
		$.ajax({
	        type: "POST",
	        dataType: "json",
	        data: { action: "delete-folder", folder_id: id},
	        success: function(json){
	            if (json.error){
	            	alert(json.error);
	            }else{
	            	//var id = $(o).attr('rel');
	            	//$('#'+id).remove();
	            	//$(o).remove();
	            	var id = $(o).attr('id');
	            	$('a[rel='+id+']').remove();
	            	$(o).remove();
	            	return true;
				}
			}
		});
		}
		return false;
	}
	gallery.deleteImage = function(o, id){
		var container = $(o).parent().parent().parent().parent().parent();
		var fid = $(container).find("input[id='album-id']").val();
		if (confirm("Вы действительно хотите удалить это фото?")){
		$.ajax({
	        type: "POST",
	        dataType: "json",
	        data: { action: "delete-image", folder_id: fid, image_id: id},
	        success: function(json){
	            if (json.error){
	            	alert(json.error);
	            }else{
	            	$(o).parent().parent().remove('');
	            	return false;
				}
			}
		});
		}
		return false;
	}
	gallery.open_tab = function(){
		var div_id = $(this).attr("rel"); 
		var container = $(this).parent().find("div[id='"+div_id+"']");
		var name = $(container).find("input[name='album-name']").val();
		var id = $(container).find("input[name='album-id']").val();
		var form = $("#add-image-form");
		$(form).find("input[name='folder']").val(id);
				
		if ($(container).find("div.items").html().replace(/(^\s+)|(\s+$)/g,"") == ''){
			$(container).find("div.pictures").addClass("empty-scrollable");
		}else{
			$(container).find("div.pictures").removeClass("empty-scrollable");
		}
   		//var str = $(this).attr("rel");
   		//alert($("#accordion").find("div#"+str).html());	   		
   	}
	gallery.make_draggable = function(){
		$("div.picture-item").each(function(){
			$(this).draggable({
				appendTo: ".album-editor",
				start: function(event, ui) {
					$("div.drop-here").show();
				},
				stop: function(event, ui) {
					$("div.drop-here").hide();
				},
				cursor: "move",
				cursorAt: {top: 0, left: -20},
				helper: function(event){
					return $('<div id="drag-label" class="drag-label">'+$(this).find("input[name='object-name']").val()+'</div>');
				}
			});
		});
	}
   	//var api = 
	gallery.openOverlay = function(){
		this.api.load();
	}/*
	gallery.openEditor = function(){
		this.eapi.load();
	}*/
	gallery.init = function(){
		this.api = $("#overlay-form").overlay({api:true, oneInstance: false, expose: '#eee', closeSpeed: 1000});
		//this.eapi = $("#image-editor").overlay({api:true, oneInstance: false, expose: '#eee', closeSpeed: 1000});
		gallery.make_draggable();
		$(".drop-here").each(function(){
			$(this).droppable({
				accept: '.picture-item',
				activeClass: 'state-hover',
				hoverClass: 'state-active',
				drop: function(event, ui) {	
					var div_id = $(this).parent().attr("rel"); 
					var container = $(this).parent().parent().find("div[id='"+div_id+"']");
					var div_id2 = $("#accordion a.current").attr("rel");					
					var container2 = $(this).parent().parent().find("div[id='"+div_id2+"']");	
					var image_id = $(ui.draggable).find("input[name='object-id']").val();
					var folder_id = $(container).find("input[name='album-id']").val();
					var cfolder_id = $(container2).find("input[name='album-id']").val();
					var to =  $(container).find("div.items");
					var item = $(container2).find("div.picture-item:has(input[value='"+image_id+"'])");	

					var div = $(this).parent();
					if (folder_id != cfolder_id) {
		//				alert(folder_id + ' ' + cfolder_id + ' ' + image_id);
						$.ajax({
					        type: "POST",
					        dataType: "json",
					        data: { 'action': 'move', 'image_id': image_id, 'folder_id': folder_id, 'cfolder_id': cfolder_id},
					        success: function(json){
					        	if (json.error){
					        		alert(json.error);
					        	}else{
					        		$(div).click();				       
									$(to).append(item);
									$(container2).find("div.items").remove(item);
									gallery.make_dragable();
					        	}
					            
					        }
						});
					}
					return true;
					
				}
			});
		});
		$("div.pictures").addClass("scrollable-withjs");
		$("div.pictures").each(function(){
			$(this).find("a[rel='lightbox']").lightBox({
				imageLoading: '/media/stylesheets/ajax_imaging/lightbox_img/lightbox-ico-loading.gif',
				imageBtnClose: '/media/stylesheets/ajax_imaging/lightbox_img/lightbox-btn-close.gif',
				imageBtnPrev: '/media/stylesheets/ajax_imaging/lightbox_img/lightbox-btn-prev.gif',
				imageBtnNext: '/media/stylesheets/ajax_imaging/lightbox_img/lightbox-btn-next.gif',
			});
		});

		$("#accordion").find("div.pane").addClass("pane-with-js");
		$("#accordion").tabs("#accordion div.pane", { 
		    tabs: 'a.handle',  
		    effect: 'slide',
		    history: true
		});
		
	   	$("#accordion a.handle").click(gallery.open_tab)
	   	$("a.handle:first").click();
	   	$("div.pictures").each(function(){
			var id = $(this).parent().find("input[name='album-id']").val();
			$(this).scrollable({next: '#next-'+id, prev: '#prev-'+id});
		});
		$("a.small-icon").hide();
		$("div.drop-here").hide();
	}
	