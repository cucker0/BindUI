/**
 * Created by 0 on 02-27.
 */

(function($){
    //自执行函数
    function getCookie(name){
        //从cookie中获取名为 csrftoken 的值并返回，默认django会response一个csrftoken值为csrf_token的cookie
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

})(jQuery);


function GetProxyServer(site_id) {
    //通过site_id 获取proxy server列表
    var data_send = {'site_id':site_id};
    $.post("/nginx/get_proxy_server/",{'data':JSON.stringify(data_send)},
            function(callback){
                var response_data = JSON.parse(callback);
                //console.log(response_data['data']);
                $('.dd-middle').html(RealServerList(response_data['data'], response_data['site_id']));
                $('.dd-right').html(ShowDu(response_data['du']));
            });
}

function RealServerList(obj, site_id){
    //源站服务器展示列表
    /*[{'proxy_server': '192.168.1.46', 'realserver': [{'url': 'http://192.168.1.46:17818/du?upstream=vip_tuandai_com_du&server=192.168.1.146:20026&up=', 'id': 2, 'host': '192.168.1.146:20026'}, {'url': 'http://192.168.1.46:17818/du?upstream=vip_tuandai_com_du&server=192.168.1.146:20026&up=', 'id': 2, 'host': '192.168.1.146:20026'}]},
        {'proxy_server': '192.168.1.142', 'realserver': [{'url': 'http://192.168.1.142:17818/du?upstream=vip_tuandai_com_du&server=192.168.1.146:20026&up=', 'id': 2, 'host': '192.168.1.146:20026'}, {'url': 'http://192.168.1.142:17818/du?upstream=vip_tuandai_com_du&server=192.168.1.146:20026&up=', 'id': 2, 'host': '192.168.1.146:20026'}]}]
    */
    var lis = '<div class="dd-subdiv"><button type="button" action="0" class="btn btn-warning" onclick="UpDown(this);">下线</button> <button type="button" action="1" class="btn btn-success pull-right" onclick="UpDown(this)">上线</button></div>';

    lis += '<table id="realserver-tab" site_id='+ site_id +' class="table table-hover"><thead><tr><th><input type="checkbox" name="ckSelectAll" status="0" onclick="SelectAll(this,\'#realserver-tab\');"></th><th>RealServer</th><th>Status</th></tr></thead><tbody>';

    for (var i in obj){
        var ele = '<tr><td><input type="checkbox" name="realserver" value="'+ obj[i].id +'" id="rs__'+  obj[i].id + '"></td><td><label for="rs__'+ obj[i].id +'">' + obj[i].ip_port + '</label></td><td>'+ UpDownStatus(obj[i].up_down) +'</td></tr>';
        lis += ele;
    }
    lis += '</tbody></table>';
    return lis;
}

function ShowDu(obj){
    //展示upstream详情
    //[{'get_du': {'192.168.1.59:20026': 1, '192.168.1.146:20026': 1}, 'proxy_server': 'nginx_11.213'}, {'get_du': {'192.168.1.59:20026': 1, '192.168.1.146:20026': 1}, 'proxy_server': 'nginx_11.211'}]
    var ele1 = '<ul class="margin-t50">';
    for (var i in obj){
        var ele2 = '<h4>'+ obj[i].proxy_server +'</h4>';
        for(var j in obj[i].get_du){
            ele2 += '<li>'+ j + UpDownStatus(obj[i].get_du[j]) + '</li>';
        }
        ele1 += ele2;
    }
    ele1 += '</ul>';
    return ele1;
}
function GetProxyServerByGroup(ths, action){
    var data_send = '';
    if (action == 0){     //刷新整个content-wrapper div
        var ele = '<div class="dd-left"><div class="site_box"></div></div><div class="dd-middle"></div><div class="dd-right"></div>';
        $('.content-wrapper').html(ele);
        //获取 proxy server by group id
        //$(".site_box").html('');
        //$(".dd-middle").html('');
        //$(".dd-right").html('');
        $(ths).parent().addClass('active');
        $(ths).parent().siblings().removeClass('active');
        var proxy_server_group_id = $(ths).attr('proxy_group_id');
        data_send = {'proxy_server_group_id':proxy_server_group_id};
    }else if (action == 1){     //只刷新dd-right div内容，适用于上、下线站点、维护站点时用
        var proxy_server_group_id = $(ths).attr('proxy_group_id');
        data_send = {'proxy_server_group_id':proxy_server_group_id};
    }else if (action == 2){     //点击分页
        var proxy_server_group_id = $('#table_site').attr('proxy_group_id');
        var page = $(ths).attr('page');
        if (!page){
            page = $('.pagination li.active a').attr('page');
        }
        data_send = {'proxy_server_group_id':proxy_server_group_id, 'page':page};
    }
    $.post("/nginx/get_proxy_server_byproxyservergroup/",{'data':JSON.stringify(data_send)},
        function(callback){
            var response_data = JSON.parse(callback);
            $('.site_box').html(response_data['data']);
        }
    );
}

function UpDownStatus(status){
    //判断upstream 服务器上、下线显示状态
    var ele = ''
    if (status == '0'){
        ele = '<span class="glyphicon glyphicon-minus-sign orange"></span>';
    }else if(status == '1'){
        ele = '<span class="glyphicon glyphicon-play-circle green"></span>';
    }else{
        ele = '<span class="glyphicon glyphicon-question-sign"></span>';
    }
    return ele;
}

function UpDown(ths){
    //上线、下线源站服务器
    var action = $(ths).attr("action");
    //获取选中的服务器checkbox值
    var checkbox_val = GetCheckboxValue('#realserver-tab');
    var site_id = $('#realserver-tab').attr('site_id');
    if (checkbox_val.length > 0 && site_id.length > 0){
        var data_send = {'action':action, 'realserver_list':checkbox_val, 'site_id':site_id};
        $.post("/nginx/updown_realserver/",{'data':JSON.stringify(data_send)},
                function(callback){
                    var callback = JSON.parse(callback)['data'];
                    //console.log(callback);
                    //var site_id = $('.site_active').find('input').val();
                    var site_id = $('#realserver-tab').attr('site_id');
                    GetProxyServer(site_id);        //刷新realserver列表
                    //GetProxyServerByGroup('.treeview-menu[name=dynamic_upstream] li.active [proxy_group_id]', 1);  //刷新站点列表
                    //GetProxyServerByGroup('#table_site', 1);  //刷新站点列表
                    GetProxyServerByGroup(null, 2);  //刷新站点列表
                });
    }
}

function GetCheckboxValue(selector){
    //获取目标选择器 input checkbox 选中的值，返回为列表
    var _checkbox_val = [];
    var _target = selector + ' input:checked[name!="ckSelectAll"]';
    $(_target).each(function(){
        _checkbox_val.push($(this).val());
    });
    return _checkbox_val;
}

function SelectAll(selector){
    //选择/取消所有
    var _check_all = selector + " input[type=checkbox][data-check-all='']";
    var check_all_status = $(_check_all).is(':checked');
    var _target = selector + " input[type=checkbox][data-check-all!='']";
    if(check_all_status){
        $(_target).prop("checked",true);
    }else{
        $(_target).removeAttr("checked");
    }
}

function SiteClick(ths){
    //点击site
    $(ths).parent().addClass('site_active').siblings().removeClass('site_active');
    var site_id = $(ths).prev().children().first().val();
    GetProxyServer(site_id);
}

function Maintain(ths){
    //站点维护，挂载维护页或去恢复正常去维护页
    var action = $(ths).attr('action');     //按钮动作，0：维护， 1：恢复
    var maintain_group_id = $('.maintain_group_select ').val();
    var checkbox_val = GetCheckboxValue('#table_site');
    if (action.length != '-1' &&  checkbox_val.length > 0){   //维护页、站点必须选择
        var data_send = {'action':action, 'maintain_group_id':maintain_group_id, 'site_id_list':checkbox_val};
        data_send = JSON.stringify(data_send);
        $.post('/nginx/maintain/', {'data':data_send},
            function(callback){
                callback = JSON.parse(callback)['data'];
                if(callback){
                    //GetProxyServerByGroup('.treeview-menu[name=dynamic_upstream] li.active [proxy_group_id]', 1);   //刷新站点列表
                    GetProxyServerByGroup('#realserver-tab', 1);   //刷新站点列表
                }
                $('.dd-middle').html('');
                $('.dd-right').html('');
            });
    }
}

function Login(){
    var user = $('.login-box-body input[type="text"]').val();
    var password = $('.login-box-body input[type="password"]').val();
    var remenber_login_status = $('.login-box-body input[type="checkbox"]').prop('checked')
    var send_data = {'user':user, 'password':password, 'remenber_login_status':remenber_login_status}
    if (user.length == 0 || password.length == 0){
        $('.login-box-msg').text('用户或密码不能为空').css('color','red');
        return 0;
    }
    send_data = JSON.stringify(send_data)
    $.post('/auth/login/', {'data':send_data},
        function(callback){
            callback = JSON.parse(callback)['data'];
            if (callback['auth_status'] == '1'){  //登录成功
                location.href = callback['url'];
            }else if(callback['auth_status'] == '0'){   //登录失败
                $('.login-box-msg').text('用户或密码错误,请重新输入').css('color','red');
            }
    });

}

function ChangePassword(){
    //用户更改密码
    var current_password = $('#current_password').val().trim();
    var new_password = $('#new_password').val().trim();
    var retype_new_password = $('#retype_new_password').val().trim();
    if (current_password.length == 0){
        var msg = '当前密码不能为空';
        $('#current_password').parent().next().html(msg);
        return 0
    }else{
        $('#current_password').parent().next().html('');
    }
    if (new_password.length < 5 ){
        var msg = '新密码必须6位以上';
        $('#new_password').parent().next().html(msg);
        return 1;
    }else {
        $('#new_password').parent().next().html('');
    }
    if(retype_new_password != new_password){
        var msg = '密码不匹配';
        $('#retype_new_password').parent().next().html(msg);
        return 3;
    }else{
        $('#retype_new_password').parent().next().html('');
    }
    $.post('/auth/userprofile/1/', {'data':JSON.stringify({'current_password':current_password,'new_password':new_password})},
        function(callback){
            callback = JSON.parse(callback)['data'];
            console.log(callback);
            if (callback['auth_status'] == '1'){  //登录成功
                location.href = callback['url'];
            }else if(callback['auth_status'] == '0'){   //登录失败
                var msg = '密码修改失败, 当前密码错误';
                $('#current_password').parent().next().html(msg);
            }
        });
}

$(function(){
    //DOM加载后执行

    //添加DNS记录 Placeholder 提示
    //$(".form-horizontal select[name=type]").change(ChangePlaceholder);
    $(".form-horizontal select[name=type]").bind('change', ChangePlaceholder);

    //搜索按键
    //通过proxy_server_id与site_name搜索site
    $('#search-btn').bind('click', function(){
        var search_key = $(this).parent().siblings().first().val();
        $(this).parent().siblings().first().val('');
        var proxy_server_group_id = $('.treeview-menu .active a').attr('proxy_group_id');
        var send_data = JSON.stringify({'search_key':search_key, 'proxy_server_group_id':proxy_server_group_id});
        //console.log(send_data);
        if(search_key.trim().length <= 0){     //搜索关键字不允许为空
            return false;
        }
        $.post('/nginx/search_site/',{'data': send_data},
            function(callback){
                callback = JSON.parse(callback)['data'];
                var ele = '<div class="dd-left"><div class="site_box"></div></div><div class="dd-middle"></div><div class="dd-right"></div>';
                $('.content-wrapper').html(ele);
                $('.site_box').html(callback);
        });
    });

    //点击 上传 按钮，代替点击 上传头像的input
    $('span[func="select_upload_file"]').bind('click', function(){
        $(this).next().filter('input').click();
    });

    //上传头像文件，前面框提示PATH
    $('#startUploadBtn').change(function(){
            var file_path = $(this).val();
            $(this).parent().prev().attr('placeholder', file_path);
        }
    );

});




function UploadFile(selector, action){
    //上传文件
    if(action == 1){
         var form_data = new FormData();
        //var name = $('#startUploadBtn').val();
        //form_data.append('file', $('#startUploadBtn')[0].files[0]);
        var name = $(selector).val();
        form_data.append('file', $(selector)[0].files[0]);
        form_data.append('name', name);
        if($(selector)[0].files[0]){
            $.ajax({
                url: '/auth/userprofile/2/',
                type: 'POST',
                data: form_data,
                //告诉jQuery不要去处理发送的数据
                processData : false,
                //告诉jQuery不要去设置Content-Type请求头
                contentType : false,
                //beforeSend: function(){
                //    console.log('正上传中，请稍候');
                //},
                success: function(callback){
                    callback = JSON.parse(callback)['data'];
                    if(callback['status'] == 1){
                        //上传图片成功
                        location.href = window.location.href;
                    }else if(callback['status'] == 2){
                        $('div[func="msg_error1"]').removeClass('hide');
                        $(selector).parent().prev().attr('placeholder', '选择一个文件');
                    }else{
                        //上传图片失败
                        $(selector).parent().prev().attr('placeholder', '选择一个文件');
                    }
                },
                error: function(err){
                    console.log(err);
                }
            });
        }
    }else if(action == 2){
        //取消上传文件
        $('div[func="msg_error1"]').addClass('hide');
        $(selector).val('');
        $(selector).parent().prev().attr('placeholder', '选择一个文件');
    }
}

function UploadFileCancel(selector) {
    //取消上传文件
    $('div[func="msg_error1"]').addClass('hide');
    $(selector).val('');
    $(selector).parent().prev().attr('placeholder', '选择一个文件');
}


function ChangeNickname(selector, action){
    //修改昵称
    if(action==1){
        var nickname_current = $(selector).attr('placeholder');
        var nickname_new = $(selector).val();
        if(nickname_new.length > 0 && nickname_current != nickname_new ){
            $.post('/auth/userprofile/3/', {'data':JSON.stringify({'nickname_new':nickname_new})},
                function(callback){
                    callback = JSON.parse(callback)['data'];
                    if(callback['status'] == 1){
                        //昵称更改成功
                        location.href = window.location.href;
                    }else{
                        $(selector).parent().next().html('昵称更改失败');
                        $(selector).val('');
                    }
                }
            );
        }
    }else if(action==2){
        $(selector).val('');
    }
}

//禁止双击选中文字
//document.onselectstart=function(){return false;}

function ChangePlaceholder(){
    //添加DNS记录选择记录类型时，自动调整相应的Placeholder提示内容
    var type_val = $(".form-horizontal select[name=type]").val();
    switch(type_val){
        case 'CNAME':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写子域名（如www），不填写默认保存为@");
            $(".form-horizontal input[name=data]").attr("palceholder", "填写一个域名，例如：www.dns.com");
            $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'MX':
            $(".form-horizontal input[name=host]").attr("placeholder", "通常填写@、mail，不填写默认保存为@");
            $(".form-horizontal input[name=data]").attr("placeholder", "填写邮件服务器地址");
            $(".form-horizontal input[name=mx]").parent().parent().show();
            $(".form-horizontal input[name=mx]").val('5');
            break;
        case 'TXT':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写子域名，不填写默认保存为@");
            $(".form-horizontal input[name=data]").attr("placeholder", "填写文本，字符长度限制255");
            $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'NS':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写子域名（如www），不可填写@");
            $(".form-horizontal input[name=data]").attr("placeholder", "填写DNS域名，例如：f1g1ns1.dnspod.net");
            $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'AAAA':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写子域名，不填写默认保存为@");
            $(".form-horizontal input[name=data]").attr("placeholder", "填写一个IPv6地址，例如：ff06:0:0:0:0:0:0:c3");
            $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'SRV':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写格式为：服务.协议（如_ldap._tcp）");
            $(".form-horizontal input[name=data]").attr("placeholder", "例如：5 0 5269 example.dns.com");
            $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'PTR':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写IP主机位数字（如反向解析IP 192.168.1.11，则填写11）");
            $(".form-horizontal input[name=data]").attr("placeholder", "填写对应的正向解析域名，例如：www.dns.com.");
            $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'SOA':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写@");
            $(".form-horizontal input[name=data]").attr("placeholder", "填写一个域名，例如：ns1.dns.com.");
            $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'REDIRECT_URL':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写子域名（如www），不填写默认保存为@");
            $(".form-horizontal input[name=data]").attr("placeholder", "填写要跳转到的网址，如：http://www.qq.com");
            $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'FORWARD_URL':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写子域名（如www），不填写默认保存为@");
            $(".form-horizontal input[name=data]").attr("placeholder", "填写要跳转到的网址，如：http://www.qq.com");
            $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        default:
            // case '0':
            $(".form-horizontal input[name=host]").attr("placeholder", "填写子域名（如www），不填写默认保存为@");
            $(".form-horizontal input[name=data]").attr("palceholder", "填写一个IPv4地址，例如：8.8.8.8");
            $(".form-horizontal input[name=mx]").parent().parent().hide();

    }

}

function DnsRecordDefaultSelect(){
    //每次点击 添加记录 重置记录类型
    $(".form-horizontal input[name=mx]").parent().parent().hide();
    var _domain_name = $("div .nav h2").text();
    if (_domain_name.endsWith('in-addr.arpa')) {
        $(".form-horizontal select[name=type]").val('PTR');
        //$(".form-horizontal input[name=host]").attr("placeholder", "填写IP主机位数字（如反向解析IP 192.168.1.11，则填写11）");
        //$(".form-horizontal input[name=data]").attr("placeholder", "填写对应的正向解析域名，例如：www.dns.com.");
    }else{
        $(".form-horizontal select[name=type]").val('A');
        //$(".form-horizontal input[name=host]").attr("placeholder", "填写子域名（如www），不填写默认保存为@");
        //$(".form-horizontal input[name=data]").attr("palceholder", "填写一个IPv4地址，例如：8.8.8.8");
    }
}

function SaveAction(){
    //点击 保存按键
    var _type = $(".modal-body select[name=type]").val();
    var _host = $(".modal-body input[name=host]").val();
    var _resolution_line = $(".modal-body select[name=resolution_line]").val();
    var _data = $(".modal-body input[name=data]").val();
    var _mx = $(".modal-body input[name=mx]").val();
    var _ttl = $(".modal-body select[name=ttl]").val();
    var _zone_tag_name = $("[zone_tag_name]").text();
    var senddata = {"type":_type, "host":_host, "resolution_line":_resolution_line, "data":_data, "mx_priority":_mx, "ttl":_ttl, "zone":_zone_tag_name }

    $.ajax({
        url: "/dns/add.html",
        type: "POST",        //请求类型
        data: {'data': JSON.stringify(senddata)},
        dataType: "json",
        success: function (callback) {
            //当向服务端发起的请求执行成功完成后，自动调用
            if (callback['status'] == 200){
                location.reload(true);      //刷新当前页面
            }
        },
        error: function () {
            //当请求错误之后，自动调用
        }
    });

}


$(document).ready(function(){
    //文件加载后执行

    //点击 添加记录 按键绑定事件
    $("button[data-toggle=modal]").bind('click', DnsRecordDefaultSelect, ChangePlaceholder);

    //添加记录时点击 保存 按键绑定事件
    $(".modal-footer  button[name=_save]").bind('click', SaveAction);
});
