Carrot = {}

$(function(){
//    $('.js_ticket').click(function(){
//       document.location.href = $(this).find('.js_href a').attr('href');
//    });

    $('.js_fixed').click(function(){
        var hours = prompt('Затрачено часов:');
        if (!hours){
            return false;
        }
        var $input = $('<input type="hidden" name="hours" value="' + hours + '">')
        $(this).closest('form').append($input);
        return true;
    });


    Carrot.FixedFilter.init();
});

Carrot.FixedFilter = {
    init: function() {
        if ($('.js_fixed_filter').length)
        {
            var filter = $('<input class="fixed_filter" type="checkbox" id="fixed_filter">' +
                '<label for="fixed_filter">скрыть выполненные</label>')

            $('.js_fixed_filter').append(filter);
            $(filter[0]).change(function(){
                Carrot.FixedFilter.apply(this.checked);
            });

            if (Carrot.FixedFilter.load()) {
                $(filter[0]).attr('checked', 'checked');
            }
            $(filter[0]).change();
        }
    },

    apply: function(hide)
    {
        var tickets = $('.tickets tr.status-fixed, .tickets tr.status-rejected');

        if (hide) {
            tickets.hide();
        } else {
            tickets.show();
        };

        Carrot.FixedFilter.save(hide);
    },

    save: function(hide)
    {
        setCookie('fixed_filter', hide);
    },

    load: function()
    {
        return getCookie('fixed_filter') == 'true';
    }
}

function setCookie (name, value) {
    document.cookie = name + "=" + escape(value)
}

function getCookie(name) {
    var cookie = " " + document.cookie;
    var search = " " + name + "=";
    var setStr = null;
    var offset = 0;
    var end = 0;
    if (cookie.length > 0) {
        offset = cookie.indexOf(search);
        if (offset != -1) {
            offset += search.length;
            end = cookie.indexOf(";", offset)
            if (end == -1) {
                end = cookie.length;
            }
            setStr = unescape(cookie.substring(offset, end));
        }
    }
    return(setStr);
}