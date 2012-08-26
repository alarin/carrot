Carrot = {}

$(function(){
    $('.js_ticket').click(function(){
       document.location.href = $(this).find('.js_href a').attr('href');
    });
});