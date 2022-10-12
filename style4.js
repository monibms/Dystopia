$(function(){
	$('.toggle_title').click(function(){
		$(this).toggleClass('selected');
		$(this).next().slideToggle();
	});
});
