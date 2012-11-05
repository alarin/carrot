$(function(){
    init_multi_file();
});

function init_multi_file()
{
    var $inputs = $('.js_multi_file');

    if ($inputs.length)
    {
        var $plus = $("<button class='js_addfile' style='display: block;'>+ Еще файл...</button>");
        $inputs.after($plus);
        $plus.click(function(){
            var $newinput = $($inputs.get(0)).clone();
            $plus.before($newinput);
            return false;
        });
    }
}