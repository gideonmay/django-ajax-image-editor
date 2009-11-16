var crop_img_size = {
	width: 0,
	height: 0
};
function previewAvatar(img, selection) {
}
function updateValues(img, selection) {
	$("input[name='left']").val(selection.x1);
	$("input[name='top']").val(selection.y1);
	$("input[name='right']").val(selection.x2);
	$("input[name='bottom']").val(selection.y2);
}

$(document).ready(function(){
	$("#image").load(function() {

		//calculate source image size
		crop_img_size.width = $('#image').width();
		crop_img_size.height = $('#image').height();

		// calculate initial selection (maximum square)
		var selection = {
			x1: 0, x2: 0, y1: 0, y2: 0,
			width: 0, height: 0
		}
		if (crop_img_size.width > crop_img_size.height) {
			selection.width = selection.height = crop_img_size.height;
			var diff = (crop_img_size.width - crop_img_size.height) / 2;
			selection.x1 = diff;
			selection.x2 = crop_img_size.width - diff;
			selection.y2 = crop_img_size.height;
		} else {
			selection.width = selection.height = crop_img_size.width;
			var diff = (crop_img_size.height - crop_img_size.width) / 2;
			selection.x2 = crop_img_size.width;
			selection.y1 = diff;
			selection.y2 = crop_img_size.height - diff;
		}
		/*
		// prepare avatarimg and its container
		$('#avatarimg_container').css({
			position: 'relative',
			overflow: 'hidden',
			width: '96px',
			height: '96px',
			margin: 'auto',
			padding: '1px'
		});
		$('#avatarimg').attr('src', $("#cropimage").attr('src')).css({
			position: 'relative'
		}).removeClass('border');

		// simulate a first preview with initial selection
		previewAImageEditor.vatar($("#cropimage"), selection);
	*/
		// run imgAreaSelect
		$("#image").imgAreaSelect({
			handles: 'corners',
			minHeight: "96",
			minWidth: "96",
			x1: selection.x1,
			x2: selection.x2,
			y1: selection.y1,
			y2: selection.y2,
			onSelectChange: previewAvatar,
			onSelectEnd: updateValues
		});
	});
});