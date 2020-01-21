/**
* 专门用于 AJAX post提交时自动处理csrftoken
*
* 自动从cookies中获取 csrftoken并自动添把获取的 csrftoken添加到RequestHeader中
*/
(function (jq) {

    /**
     * 从cookie中获取名为 csrftoken 的值并返回
     *
     * 默认django会response一个csrftoken值为csrf_token的cookie
     *
     * @param name: cookie名
     * @returns: 获取的cookie值
     */
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');
    //The above code could be simplified by using the JavaScript Cookie library to replace getCookie:　
    // need include js.cookie.js
    //var csrftoken = Cookies.get('csrftoken');
    //console.log(csrftoken)

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // 设置ajax发送前执行的方法，这是全局生效的
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) { // !this.crossDomain 表示不跨域
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                //console.log(csrftoken);
            }
        }
    });

})(jQuery);

