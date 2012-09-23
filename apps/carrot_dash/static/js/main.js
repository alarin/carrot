Carrot = {}

$(function(){
    $('.js_ticket').click(function(){
       document.location.href = $(this).find('.js_href a').attr('href');
    });

    $('.js_fixed').click(function(){
        var hours = prompt('Затрачено часов:');
        if (!hours){
            return false;
        }
        var $input = $('<input type="hidden" name="hours" value="' + hours + '">')
        $(this).closest('form').append($input);
        return true;
    })
});