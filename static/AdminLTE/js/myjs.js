/**
 * Created by 0 on 02-27 2016.
 */

function GetCheckboxValue(selector){
    //获取目标选择器 input checkbox 选中的值，返回为列表
    var _checkbox_val = [];
    //var _target = selector + ' input:checked[name!="ckSelectAll"]';
    var _target = selector + ' input:checked:not([data-check-all])';
    $(_target).each(function(){
        _checkbox_val.push($(this).val());
    });
    return _checkbox_val;
}


function SelectAll(){
    //选择/取消所有项
    var check_all_status = $(this).is(':checked');
    var _tag_input = $(this).parent().parent().parent().siblings().find("input");

    if(check_all_status){
        $(_tag_input).prop("checked",true);
    }else{
        $(_tag_input).removeAttr("checked");
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
    //$.post('/auth/login/', {'data':send_data},
    $.post(window.location.pathname + window.location.search, {'data':send_data},
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
            //console.log(callback);
            if (callback['auth_status'] == '1'){  //登录成功
                location.href = callback['url'];
            }else if(callback['auth_status'] == '0'){   //登录失败
                var msg = '密码修改失败, 当前密码错误';
                $('#current_password').parent().next().html(msg);
            }
        });
}

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

function UploadImportDNSFile(){
    //上传导入DNS文件
     var form_data = new FormData();
    var selector = $('input[name=import_dns_file]')
    //var name = $(selector).val();
    form_data.append('file', $(selector)[0].files[0]);
    //form_data.append('name', name);
    var _url = document.URL;
    if ($(selector)[0].files[0]){
        $.ajax({
            url: _url,
            type: 'POST',
            data: form_data,
            //告诉jQuery不要去处理发送的数据
            processData : false,
            //告诉jQuery不要去设置Content-Type请求头
            contentType : false,
            //beforeSend: function(){
            //    console.log('正上传中，请稍候');
            //},
            //async: false,
            success: function(callback){
                $("#table_import_dns").html(callback);
            },
            error: function(err){
                console.log(err);
            }
        });
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

function MXShowOrHide(){
    //DNS MX input展示或隐藏
    var type_val = $(".form-horizontal select[name=type]").val();
    switch(type_val){
        case 'MX':
            $(".form-horizontal input[name=mx]").parent().parent().show();
            var _mx = $(".form-horizontal input[name=mx]").val();
            if (_mx != '' || _mx != undefined){
                $(".form-horizontal input[name=mx]").val('10');
            }
            $(".form-horizontal input[name=data]").prop("placeholder", "填写邮件服务器地址，如：mx2.dns.com.");
            break;
        default:
            $(".form-horizontal input[name=mx]").val('');
            $(".form-horizontal input[name=mx]").parent().parent().hide();

    }
}

function RedirectCodeShowOrHide() {
    // 添加 显性URL 时，重定向 code 选择框的展示/隐藏
    var type_val = $(".form-horizontal select[name=type]").val();

    switch (type_val) {
        case 'EXPLICIT_URL':
            $(".form-horizontal select[name=redirect_code]").show();
            break;
        default:
            $(".form-horizontal select[name=redirect_code]").hide();
    }
}

function ChangePlaceholder(){
    var action_type = $("#DNSRecordAddOrModifyModalLabel").prop("action_type");
    if(action_type == "add"){       // 添加记录，清空host，data值
        $(".form-horizontal input[name=host]").val("");
        $(".form-horizontal input[name=data]").val("");
        $(".form-horizontal input[name=comment]").val("");
    }

    // 添加DNS记录选择记录类型时，自动调整相应的Placeholder提示内容
    var type_val = $(".form-horizontal select[name=type]").val();
    MXShowOrHide();
    RedirectCodeShowOrHide();

    switch(type_val){
        case 'CNAME':

            $(".form-horizontal input[name=host]").prop("placeholder", "填写子域名（如www），不填写默认保存为@");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写一个域名，例如：www.dns.com.");
            break;
        case 'MX':
            $(".form-horizontal input[name=host]").prop("placeholder", "通常填写@、mail，不填写默认保存为@");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写邮件服务器地址，如：mx2.dns.com.");
            break;
        case 'TXT':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写子域名，不填写默认保存为@");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写文本，字符长度限制255，如：v=spf1 include:spf.mail.qq.com -all");
            //$(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'NS':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写子域名（如www），不可填写@");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写DNS域名，例如：f1g1ns1.dnspod.net.");
            break;
        case 'AAAA':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写子域名，不填写默认保存为@");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写一个IPv6地址，例如：ff06:0:0:0:0:0:0:c3");
            break;
        case 'SRV':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写格式为：服务.协议（如_ldap._tcp）");
            $(".form-horizontal input[name=data]").prop("placeholder", "格式为：优先级 权重 端口 主机名，例如：5 0 5269 example.dns.com.");
            break;
        case 'PTR':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写IP主机位数字（如反向解析IP 192.168.1.11，则填写11）");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写对应的正向解析域名，例如：www.dns.com.");
            break;
        case 'SOA':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写@");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写一个域名，例如：ns1.dns.com.");
            break;
        case 'CAA':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写子域名（如www），不填写默认保存为@");
            $(".form-horizontal input[name=data]").prop("placeholder", '填写tag-value 标签-值 对,如：0 issue "ca.abc.com"，参考https://sslmate.com/caa/');
            break;
        case 'URI':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写子域名（如www），格式：_service._proto，如：_ftp._tcp");
            $(".form-horizontal input[name=data]").prop("placeholder", '格式：priority weight "target"，如：10 1 "ftp://ftp1.example.com/public"');
            break;
        case 'EXPLICIT_URL':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写子域名（如www），不填写默认保存为@");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写要跳转到的网址，如：http://www.qq.com");
            break;
        case 'IMPLICIT_URL':
            $(".form-horizontal input[name=host]").prop("placeholder", "填写子域名（如www），不填写默认保存为@");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写要跳转到的网址，如：https://www.qq.com");
            break;
        default:
            $(".form-horizontal input[name=host]").prop("placeholder", "填写子域名（如www），*表示泛域名，不填写默认保存为@");
            $(".form-horizontal input[name=data]").prop("placeholder", "填写一个IPv4地址，例如：8.8.8.8");
            //$(".form-horizontal input[name=mx]").parent().parent().hide();
    }

}

function ClearRecordAddModModal(){
    // 清空 DNS记录 添加/修改 模态框一些历史值
    $(".modal-body select[name=type]").val('A');
    $(".modal-body input[name=host]").val('');
    $(".modal-body select[name=resolution_line]").val(0);
    $(".modal-body input[name=data]").val('');
    $(".modal-body input[name=mx]").val('');
    $(".modal-body select[name=ttl]").val(600);
    $(".modal-body input[name=comment]").val('');
}

function RecordAddACK(){
    // 添加DNS记录确认操作页面
    $("#DNSRecordAddOrModifyModalLabel .modal-title").html("添加记录");         //修改modal标题内容
    $("#DNSRecordAddOrModifyModalLabel").attr("action_type", "add");        //修改 action_type值

    //每次点击 添加记录 重置记录类型,并改变Placeholder值
    $(".form-horizontal input[name=mx]").parent().parent().hide();
    $(".form-horizontal input[name=host]").val('');
    $(".form-horizontal select[name=resolution_line]").val('0');
    $(".form-horizontal input[name=data]").val('');
    $(".form-horizontal select[name=ttl]").val('600');
    $(".form-horizontal input[name=comment]").val('');
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
    ChangePlaceholder();
}

function RecordAddModify(){
    // 添加记录/修改记录 点击 保存按键
    var _type = $(".modal-body select[name=type]").val().trim();
    var _host = $(".modal-body input[name=host]").val().trim();
    var _resolution_line = $(".modal-body select[name=resolution_line]").val().trim();
    var _data = $(".modal-body input[name=data]").val().trim();
    var _mx = $(".modal-body input[name=mx]").val().trim();
    var _ttl = $(".modal-body select[name=ttl]").val().trim();
    var _zone_tag_name = $("#table_record_list").attr("domain").trim();
    var _comment = $(".modal-body input[name=comment]").val().trim();
    var _redirect_code = $(".modal-body select[name=redirect_code]").val().trim();
    var __data = {"type":_type, "host":_host, "resolution_line":_resolution_line, "data":_data, "mx_priority":_mx, "ttl":_ttl, "comment":_comment, "zone":_zone_tag_name };

    // 显性URL，添加额外的 redirect_code
    switch (__data.type) {
        case "EXPLICIT_URL":
            __data.type = 'TXT';
            __data.basic = parseInt(_redirect_code);
            break;
        case "IMPLICIT_URL":
            __data.type = 'TXT';
            __data.basic = 200;
    }

    // 参数检测
    if (__data.data == "") {
        console.log("记录值不能为空!")
        return
    } else if (__data.host == "") {
        __data.host =  '@'
    }
    var action_type = $("#DNSRecordAddOrModifyModalLabel").attr("action_type");
    if (action_type == "add"){  //添加记录
        var record_set = [];
        record_set.push(__data);
        $.ajax({
            url: "/dns/add.html",
            type: "POST",        //请求类型
            data: {'data': JSON.stringify(record_set)},
            dataType: "json",
            success: function (callback) {
                //当向服务端发起的请求执行成功完成后，自动调用
                if (callback['status'] == 200){     //刷新当前页面,status=500 添加记录失败。
                    $("#DNSRecordAddOrModifyModalLabel").modal('hide');
                    ClickPage( { 'data':{'optype':5} } );       // 分页器中查看最后一页
                    //location.reload(true);
                }
            },
            error: function () {
                //当请求错误之后，自动调用
            }
        });
    } else if (action_type == "modify"){        //修改记录
        var _id = $("#DNSRecordAddOrModifyModalLabel .modal-title").prop("id");
        $("#DNSRecordAddOrModifyModalLabel .modal-title").removeProp("id");
        __data['id'] = _id;
        //var history_search_key = $("#table_record_list").attr("history_search_key");
        //var _history_search_key = $("#table_record_list").attr("history_search_key").trim();
        $.ajax({
            url: "/dns/mod.html?type=main",
            type: "POST",        //请求类型
            data: {'data': JSON.stringify(__data)},
            dataType: "json",
            success: function (callback) {
                //当向服务端发起的请求执行成功完成后，自动调用
                if (callback['status'] == 200){ //刷新当前页面,status=500 添加记录失败。
                    //location.reload(true);
                    $("#DNSRecordAddOrModifyModalLabel").modal('hide');
                    ClickPage( { 'data':{'optype':3} } );
                    //if(_history_search_key == ""){
                    //    ClickPage( { 'data':{'optype':3} } );
                    //}else{
                    //    ClickPage( { 'data':{'optype':6} } );
                    //}

                    ClearRecordAddModModal();
                }
            },
            error: function () {
                //当请求错误之后，自动调用
            }
        });
    }


}

function ImportDnsRecordACK(){
    // 批量导入DNS记录
    var record_set = [];
    var _zone_tag_name = $("p[name=import_dns_domain]").attr("domain").trim();
    $("#table_import_dns tbody tr").each(function(){
        var _record = {};
        _record['host'] = $($(this).find('td')).children()[0].value.trim();
        _record['type'] = $($(this).find('td')).children()[1].value.trim();
        _record['data'] = $($(this).find('td')).children()[2].value.trim();
        _record['ttl'] = $($(this).find('td')).children()[3].value.trim();
        _record['resolution_line'] = $($(this).find('td')).children()[4].value.trim();
        _record['comment'] = $($(this).find('td')).children()[5].value.trim();
        _record['zone'] = _zone_tag_name;
        record_set.push(_record);
    });
    //console.log(record_set);
    if(record_set.length > 0){
       $.ajax({
            url: "/dns/add.html",
            type: "POST",        //请求类型
            data: {'data': JSON.stringify(record_set)},
            dataType: "json",
            success: function (callback) {
                //当向服务端发起的请求执行成功完成后，自动调用
                if (callback['status'] == 200){     //刷新当前页面,status=500 添加记录失败。
                    $("#table_import_dns").html('');
                }
            },
            error: function () {
                //当请求错误之后，自动调用
                $("#table_import_dns").html('');
            }
        });
    }
}

function ExportDnsRecord(){
    // 点击导出DNS解析记录
    $('#ExportDnsRecordModalLabel').modal('show');
    var _domain = $($(this).parent().parent().parent().parent().siblings()[1]).html();
    var _modal_title = $("#ExportDnsRecordModalLabel h4").html();
    _modal_title = _domain + ' ' +  _modal_title;

    $("#ExportDnsRecordModalLabel h4").html(_modal_title);
    $("#ExportDnsRecordModalLabel h4").attr('domain', _domain);



}

function ExportDnsRecordACK(){
    // 确认导出DNS解析记录
    var _export_dns_record_type = $("select[name=export_dns_record_type]")[0].value.trim();
    var _zone = $("#ExportDnsRecordModalLabel h4").attr('domain')
    var __data = {'export_dns_record_type': _export_dns_record_type, 'zone':_zone}

    var url = "/domains/_export_dns.html?data=" + JSON.stringify(__data);

    $.ajax({
        url: "/domains/_export_dns.html",
        type: "POST",        //请求类型
        data: {},
        //async : false,
        dataType: "json",
        //beforeSend:function(XMLHttpRequest){
        //    // 请求前执行
        //},
        success: function (response, status, request) {
            //当向服务端发起的请求执行成功完成后，自动调用
            if(request['status'] == 200){
                $('#ExportDnsRecordModalLabel').modal('hide');
                $("select[name=export_dns_record_type]").val('0')
                window.location.href = url;     //下载文件
            }
        },
        error: function () {
            //当请求错误之后，自动调用
        }
    });
}

function  GetCheckboxAttrSet(selector, attr){
    //获取checkbox 属性集合值, 返回为列表
    var _set = [];
    var _tag_selector =  selector + " input:checked:not([data-check-all])";
    $(_tag_selector).each(function () {
        _set.push($(this).prop(attr));
    });
    return _set;
}

function RecordDelteACK(event){
    //记录删除确认，显示删除记录模态对话框(删除确认)
    if(event.data.optype == 1){ // 单条记录操作
        var tag_selector = $(this).parent().siblings().filter("input, :first");     //<td>...</td>
        tag_selector.children().prop("checked", true);      //当前行打勾
        tag_selector.parent().siblings().find('input').removeAttr("checked");       //取消其他行的勾
        $(this).parent().parent().parent().prev().find("input").removeAttr("checked");    //取消 selectAll 勾
        $("DNSRecordDeleteModalLabel").prop("multiple", 0);     // 标识为非多条操作
    }else if (event.data.optype == 2){
        $("DNSRecordDeleteModalLabel").prop("multiple", 1);     // 标识为多条操作
    }

    $('#DNSRecordDeleteModalLabel').modal('show');
}

function RecordDel(){
    //删除DNS记录（执行删除）
    var _checkbox_val = [];
    var multiple = $("DNSRecordDeleteModalLabel").prop("multiple");
    if(multiple == 0){     // 单条操作
        var select_id = $("#table_record_list tbody input:checked").prop('id');
        _checkbox_val.push(select_id);
    } else {  // 多条操作
        //$("#table_record_list input:checked:not([data-check-all])").each(function () {
        //    _checkbox_val.push($(this).attr("id"));
        //});
        _checkbox_val = GetCheckboxAttrSet("#table_record_list", "id")
    }

    $.ajax({
        url: "/dns/del.html",
        type: "POST",        //请求类型
        data: {'data': JSON.stringify(_checkbox_val)},
        dataType: "json",
        success: function (callback) {
            //当向服务端发起的请求执行成功完成后，自动调用
            if (callback['status'] == 200) {
                //location.reload(true);      //刷新当前页面,status=500 添加记录失败。
                $("#DNSRecordDeleteModalLabel").modal('hide');
                ClickPage({'data':{'optype':3}});
            }
        },
        error: function () {
            //当请求错误之后，自动调用
        }
    });
}

function RecordStatusACK(event){
    //DNS记录状态修改确认操作页面
    if(event.data.optype == 1){     //单条操作
        var tag_selector = $(this).parent().siblings().filter("input, :first");     //<td>...</td>
        tag_selector.children().prop("checked", true);      //当前行打勾
        tag_selector.parent().siblings().find('input').removeAttr("checked");       //取消其他行的勾
        $(this).parent().parent().parent().prev().find("input").removeAttr("checked");    //取消 selectAll 勾
        $("#DNSRecordStatusModalLabel").prop("multiple", 0);
    } else if(event.data.optype == 2){      //多条操作
        $("#DNSRecordStatusModalLabel").prop("multiple", 1);
    }
    var _status = $(this).prop('name');
    $("#DNSRecordStatusModalLabel").prop('name', _status);      // 在DNS记录状态操作模态框中标识 DNS记录状态操作动态类型
    if (_status == '_turnOff'){
        $("#DNSRecordStatusModalLabel td .info").text('暂停记录吗？');
    } else if(_status == '_turnOn'){
        $("#DNSRecordStatusModalLabel td .info").text('开启记录吗？');
    }
    $('#DNSRecordStatusModalLabel').modal('show');
}

function RedcordStatusModify(){
    // 修改记录状态
    var _checkbox_val = [];
    var _action = '';
    var multiple = $("#DNSRecordStatusModalLabel").prop("multiple");
    //var _history_search_key = $("#table_record_list").attr("history_search_key").trim();
    if(multiple == 0){
        var select_id = $("#table_record_list tbody input:checked").prop('id');
        _checkbox_val.push(select_id);
        //_action = $("#table_record_list tbody tr").has(":checked").find('a[action_type=status]').attr('name');
        _action = $(this).prop('name');
    }else if(multiple == 1){
        _checkbox_val = GetCheckboxAttrSet("#table_record_list", 'id');
        _action = $("#DNSRecordStatusModalLabel").prop('name');
    }
    _checkbox_val = GetCheckboxAttrSet("#table_record_list", 'id');
    _action = $("#DNSRecordStatusModalLabel").prop('name');


    var data = {'action':_action, 'id_list':_checkbox_val};

    $.ajax({
        url:"/dns/mod.html?type=status",
        type:"POST",
        data:{'data':JSON.stringify(data)},
        dataType:"json",
        success:function(callback){
            if (callback['status']  == 200){        // 状态修改成功
                //location.reload(true);
                $("#DNSRecordStatusModalLabel").modal('hide');
                //if(_history_search_key == ""){
                //    ClickPage({'data':{'optype':3}});
                //}else {
                //    ClickPage({'data':{'optype':6}});
                //}
                ClickPage({'data':{'optype':3}});

            }
        },
        error:function(){

        }
    });
}

function RecordModifyACK(){
    //DNS记录修改确认操作页面
    $("#DNSRecordAddOrModifyModalLabel .modal-title").html("修改记录");     //修改modal标题内容
    $("#DNSRecordAddOrModifyModalLabel").attr("action_type", "modify");        //修改 action_type值

    $('#DNSRecordAddOrModifyModalLabel').modal('show');
    var _tag_selector = $(this).parent().siblings();
    var _id = $(_tag_selector[0]).children().attr("id");
    var _host = $(_tag_selector[1]).children('span').text();
    var _type = $(_tag_selector[2]).text();
    var _resolution_line = $(_tag_selector[3]).attr("line");
    var _data = $(_tag_selector[4]).children('span').text();
    var _mx_priority = $(_tag_selector[5]).text();
    var _ttl = $(_tag_selector[6]).attr("ttl");
    var _comment = $(_tag_selector[9]).text();
    var _basic_code = $(_tag_selector[2]).attr("basic_code");

    if (_type === '显性URL') {
        _type = 'EXPLICIT_URL';
        $(".form-horizontal select[name=redirect_code]").val(_basic_code);
    } else if (_type === '隐性URL') {
        _type = 'IMPLICIT_URL';
    }

    $(".form-horizontal input[name=host]").val(_host);
    $(".form-horizontal select[name=type]").val(_type);
    $(".form-horizontal select[name=resolution_line]").val(_resolution_line);
    $(".form-horizontal input[name=data]").val(_data);
    $(".form-horizontal input[name=mx]").val(_mx_priority);
    $(".form-horizontal select[name=ttl]").val(_ttl);
    $(".form-horizontal input[name=comment]").val(_comment);
    $("#DNSRecordAddOrModifyModalLabel .modal-title").prop("id", _id);

    MXShowOrHide();
    RedirectCodeShowOrHide();
}

function ClickPage(event){
    //点击分页
    // event ==> { 'data': {'optype': 1} }
    // event.data 为含操作类型字典 ==> { 'optype': 1 }
    var page_num = 1;
    var active_page_num = parseInt( $(".pagination li.active a").text().trim() ) || 1;
    var _action = 'pagination';     // 点击分页(搜索还是点击分页)
    var _other = {};        // 其他参数
    //var _history_search_key = $("#table_record_list").attr("history_search_key").trim();
    var _search_key = $("input[name=dns_record_search]").val().trim();
    //_other['history_search_key'] = _history_search_key;
    if (event.data.optype == 1){        // 点击分页导航器上的分页码

        if ( typeof($(this).attr("aria-label")) != "undefined" ){
            if ($(this).parent().hasClass("disabled")){     // 上一页、下一页若为 disabled 直接退出
                return 400;
            }

            var PN = $(this).attr("aria-label");
            if (PN == "Previous"){      // 查看上一页
                page_num = active_page_num - 1;
            } else if (PN == "Next"){       // 查看下一页
                page_num = active_page_num + 1;
            }
        } else{
            page_num = $(this).text().trim();
            if (!parseInt(page_num)){
                console.log("page number is error!");
                return 400;
            }
        }


    }else if (event.data.optype == 2){      // 点击分页导航器上输入页码直接跳转
        page_num = $("#input_page").val().trim();
        $(this).prev().val('');
        if (!parseInt(page_num)){
            console.log("page number is error!");
            return 400;
        }
    }else if(event.data.optype == 3){       // 刷新当前分页（如修改了记录状态后刷新回本分页）
        page_num = active_page_num;
    }else if(event.data.optype == 4){       // 搜索record记录
        _action = 'search';     // 搜索分页(搜索还是点击分页)
        //_other = {'search_key':event.data.search_key};
    }else if(event.data.optype == 5){       // 查看最后一页
        page_num = 0;
    }else if(event.data.optype == 6){       // 修改搜索的record记录及其状态
        _action = 'search';
        //_other = {'search_key':_history_search_key};
    }

    var perpage_num = $("#perpage-dropdownMenu").attr('value') || 10;
    var active_page = $(".pagination .active").text() || 1;

    _other = {'search_key':_search_key};
    if (page_num != active_page || (event.data.optype != 1) || (event.data.optype != 2)){
        var _zone_tag_name = $("#table_record_list").attr("domain").trim();

        var __data = {'action':_action, 'page':page_num, 'zone':_zone_tag_name, 'perpage_num':perpage_num, 'other':_other}
        //console.log(__data);
        var html = $.ajax({
            url: "/dns/rlist_page.html",
            type:"POST",
            data:{'data':JSON.stringify(__data)},
            dataType:"json",
            async: false,
        }).responseText;
        $("#domain_record_box").html(html);
        //$(".pagination a").bind('click', ClickPage)
    }

}

function DomainResolutionPage(event){
    // 域名解析列表分页
    // event ==> { 'data': {'optype': 1} }
    // event.data 为含操作类型字典 ==> { 'optype': 1 }
    var page_num = 1;
    var active_page_num = parseInt( $(".pagination li.active a").text().trim() ) || 1;
    var _action = 'pagination';     // 点击分页(搜索还是点击分页)
    var _other = {};        // 其他参数

    if (event.data.optype == 1){        // 点击分页导航器上的分页码

        if ( typeof($(this).attr("aria-label")) != "undefined" ){
            if ($(this).parent().hasClass("disabled")){     // 上一页、下一页若为 disabled 直接退出
                return 400;
            }

            var PN = $(this).attr("aria-label");
            if (PN == "Previous"){      // 查看上一页
                page_num = active_page_num - 1;
            } else if (PN == "Next"){       // 查看下一页
                page_num = active_page_num + 1;
            }
        } else{
            page_num = $(this).text().trim();
            if (!parseInt(page_num)){
                console.log("page number is error!");
                return 400;
            }
        }


    }else if (event.data.optype == 2){      // 点击分页导航器上输入页码直接跳转
        page_num = $("#input_page").val().trim();
        $(this).prev().val('');
        if (!parseInt(page_num)){
            console.log("page number is error!");
            return 400;
        }
    }else if(event.data.optype == 3){       // 刷新当前分页（如修改了记录状态后刷新回本分页）
        page_num = active_page_num;
    }else if(event.data.optype == 4){       // 搜索record记录
        _action = 'search';     // 搜索分页(搜索还是点击分页)
        _other = {'search_key':event.data.search_key};
    }else if(event.data.optype == 5){       // 查看最后一页
        page_num = 0;
    }

    var perpage_num = $("#perpage-dropdownMenu").attr('value') || 10;
    var active_page = $(".pagination .active").text() || 1;

    if (page_num != active_page || (event.data.optype != 1) || (event.data.optype != 2)){

        var __data = {'action':_action, 'page':page_num, 'perpage_num':perpage_num, 'other':_other};
        //console.log(__data);
        var html = $.ajax({
            url: "/domains/drlist_page.html",
            type:"POST",
            data:{'data':JSON.stringify(__data)},
            dataType:"json",
            async: false,
        }).responseText;
        $("#domain_resolution_box").html(html);

    }
}

function DomainPage(event){
    // 我的域名 分页
    // event ==> { 'data': {'optype': 1} }
    // event.data 为含操作类型字典 ==> { 'optype': 1 }
    var page_num = 1;
    var active_page_num = parseInt( $(".pagination li.active a").text().trim() ) || 1;
    var _action = 'pagination';     // 点击分页(搜索还是点击分页)
    var _other = {};        // 其他参数

    if (event.data.optype == 1){        // 点击分页导航器上的分页码

        if ( typeof($(this).attr("aria-label")) != "undefined" ){
            if ($(this).parent().hasClass("disabled")){     // 上一页、下一页若为 disabled 直接退出
                return 400;
            }

            var PN = $(this).attr("aria-label");
            if (PN == "Previous"){      // 查看上一页
                page_num = active_page_num - 1;
            } else if (PN == "Next"){       // 查看下一页
                page_num = active_page_num + 1;
            }
        } else{
            page_num = $(this).text().trim();
            if (!parseInt(page_num)){
                console.log("page number is error!");
                return 400;
            }
        }


    }else if (event.data.optype == 2){      // 点击分页导航器上输入页码直接跳转
        page_num = $("#input_page").val().trim();
        $(this).prev().val('');
        if (!parseInt(page_num)){
            console.log("page number is error!");
            return 400;
        }
    }else if(event.data.optype == 3){       // 刷新当前分页（如修改了记录状态后刷新回本分页）
        page_num = active_page_num;
    }else if(event.data.optype == 4){       // 搜索record记录
        _action = 'search';     // 搜索分页(搜索还是点击分页)
        _other = {'search_key':event.data.search_key};
    }else if(event.data.optype == 5){       // 查看最后一页
        page_num = 0;
    }

    var perpage_num = $("#perpage-dropdownMenu").attr('value') || 10;
    var active_page = $(".pagination .active").text() || 1;

    if (page_num != active_page || (event.data.optype != 1) || (event.data.optype != 2)){

        var __data = {'action':_action, 'page':page_num, 'perpage_num':perpage_num, 'other':_other};
        //console.log(__data);
        var html = $.ajax({
            url: "/domains/dlist_page.html",
            type:"POST",
            data:{'data':JSON.stringify(__data)},
            dataType:"json",
            async: false,
        }).responseText;
        $("#domain_box").html(html);
    }
}

function SelectPerPageNum(){
    //选择x条记录/页
    var perpage_num = $(this).parent().attr("value");
    var perpage_text = $(this).parent().text().trim();
    $("#perpage-dropdownMenu").attr("value", perpage_num);
    $("#perpage-dropdownMenu span:first").text(perpage_text)

    ClickPage({'data':{'optype': 0}});
}

function DomainSelutionSelectPerPageNum(){
    // 域名解析列表页选择 分页x条记录/页
    var perpage_num = $(this).parent().attr("value");
    var perpage_text = $(this).parent().text().trim();
    $("#perpage-dropdownMenu").attr("value", perpage_num);
    $("#perpage-dropdownMenu span:first").text(perpage_text)

    DomainResolutionPage({'data':{'optype': 0}});
}

function DomainSelectPerPageNum(){
    // 域名解析列表页选择 分页x条记录/页
    var perpage_num = $(this).parent().attr("value");
    var perpage_text = $(this).parent().text().trim();
    $("#perpage-dropdownMenu").attr("value", perpage_num);
    $("#perpage-dropdownMenu span:first").text(perpage_text)

    DomainPage({'data':{'optype': 0}});
}

function DnsRecordSearch(){
    // DNS记录搜索
    var _search_key = $("input[name=dns_record_search]").val().trim();
    //$("input[name=dns_record_search]").val('');

    ClickPage({'data':{'optype':4, 'search_key':_search_key} });
}

function DomainResolutionSearch(){
    // 域名解析页搜索
    var _search_key = $("input[name=domain_resolution_search]").val().trim();
    $("input[name=domain_resolution_search]").val('');

    DomainResolutionPage({'data':{'optype':4, 'search_key':_search_key} });
}

function DomainSearch(){
    // 我的域名页搜索
    var _search_key = $("input[name=domain_search]").val().trim();
    $("input[name=domain_search]").val('');

    DomainPage({'data':{'optype':4, 'search_key':_search_key} });
}

function EnterdSearch(){
    // 按下回车键的事件
    document.onkeydown = function (e) {
        var _event = e || window.event;
        if (_event.keyCode == 13) {
            //if (document.activeElement.name == 'dns_record_search'){
            //    DnsRecordSearch();
            //} else if (document.activeElement.name == 'domain_resolution_search'){
            //    DomainResolutionSearch();
            //}
            switch (document.activeElement.name) {
                case 'dns_record_search':
                    DnsRecordSearch();
                    break;
                case 'domain_resolution_search':
                    DomainResolutionSearch();
                    break;
                case 'domain_search':
                    DomainSearch();
                    break;
                case 'input_page_number':
                    ClickPage({ 'data': {'optype': 2}});
                    break;
            }
        }
    }
}

function DoaminAddACK(){
    // 添加域名确认操作页面
    $("#DomainAddOrModifyModalLabel").modal("show");
    $("#DomainAddOrModifyModalLabel .modal-title").html("添加域名");  // 修改modal标题内容
    $("#DomainAddOrModifyModalLabel").attr("action_type", "add");  // 修改 action_type值
}

function DoaminAdd(){
    //添加域名 点击 保存按键

    var _zone = $("#DomainAddOrModifyModalLabel input[name=zone]").val().trim();
    var _data = $("#DomainAddOrModifyModalLabel input[name=data]").val().trim();
    var _responsible_mail = $("#DomainAddOrModifyModalLabel input[name=responsible_mail]").val().trim();
    //var _serial = $("#DomainAddOrModifyModalLabel input[name=serial]").val().trim();
    var _refresh = $("#DomainAddOrModifyModalLabel input[name=refresh]").val().trim();
    var _retry = $("#DomainAddOrModifyModalLabel input[name=retry]").val().trim();
    var _expire = $("#DomainAddOrModifyModalLabel input[name=expire]").val().trim();
    var _minimum = $("#DomainAddOrModifyModalLabel input[name=minimum]").val().trim();
    var _primary_ns = $("#DomainAddOrModifyModalLabel input[name=primary_ns]").val().trim();
    var _comment = $("#DomainAddOrModifyModalLabel input[name=comment]").val().trim();

    var _data = {
        'zone': _zone,
        'data': _data,
        'resp_person': _responsible_mail,
        //'serial': _serial,
        'refresh': _refresh,
        'retry': _retry,
        'expire': _expire,
        'minimum': _minimum,
        'primary_ns': _primary_ns,
        'comment':_comment
    };

    $.ajax({
        url:"/domains/domain_curd.html?type=c",
        type:"POST",
        data:{'data':JSON.stringify(_data)},
        dataType:"json",
        success:function(callback){
            if (callback['status']  == 200){        // 状态修改成功
                $("#DomainAddOrModifyModalLabel").modal('hide');
                location.reload(true);
            }
        },
        error:function(){

        }
    });

}

function DnsResolutionClick(){
    //域名列表页点击 DNS解析跳转到DNS解析页
    var domain_id = $(this).parent().siblings().first().find("input").prop("id").trim();
    var url = "/dns/" + domain_id;
    location.href = url;
}


function DomainMan(){
    //域名列表页点击 管理跳转到DNS管理页
    var domain_id = $(this).parent().siblings().first().find("input").prop("id").trim();
    var url = "/domains/" + domain_id + "/info";
    location.href = url;
}

function AddDomainNSHtmlElement(){
    //点击 新增 域名NS 按钮添加输入框
    var element = '\
        <ul class="row"> \
            <li class="col-md-2"> </li> \
            <li class="col-md-5"><input name="ns" type="text" class="col-md-12" placeholder="NS主机，如：ns1.bindui.com."></li> \
            <a href="javascript:;" name="_domain_ns_edit_del">删除</a> \
        </ul>';
    $(this).parent().parent().parent().append(element);
}


function AddDomainNS(){
    //新建domain ns记录，输入NS主机名后，提交到后台
    var _ns_list = [];
    var ele_ul = $(this).parent().parent().siblings();
    var _zone = $(ele_ul).find("li[name=zone]").text().trim();
    $(ele_ul).find("input[name=ns]").each(function (i) {
        var _ns = $(this).val().trim();
        if ( !(_ns == '' || _ns == undefined) ){
            _ns_list.push(_ns);
        }
    });
    var __data = {'zone':_zone, 'ns_list': _ns_list};
    $.ajax({
        url:"/domains/domain_curd.html?type=ns",
        type:"GET",
        data:{'data':JSON.stringify(__data)},
        dataType:"json",
        success:function(callback){
            if (callback['status']  == 200){        // 状态修改成功
                location.reload(true);
            }
        },
        error:function(){

        }
    });
}

function DomainNsEditDel(){
    // 点击 domain ns编辑框后的 删除按钮 删除该编辑框
    $(this).parent().remove();

}

function DomainStatusACK(){
    // 修改domain状态确认框

    var tag_selector = $(this).parent().parent().parent().parent().siblings().filter("input, :first");
    $(tag_selector).children().prop('checked', true);
    $(tag_selector).parents().siblings().find("input[type=checkbox]").prop('checked', false);
    var _status = $(this).prop('name');
    $("#DomainStatusModalLabel").prop('name', _status);      // 在DNS记录状态操作模态框中标识 DNS记录状态操作动作类型
    if (_status == '_turnOff'){
        $("#DomainStatusModalLabel td .info").text(GetDomainName() + ' 域名暂停吗？');
    } else if(_status == '_turnOn'){
        $("#DomainStatusModalLabel td .info").text(GetDomainName() + ' 域名开启吗？');
    }
    $("#DomainStatusModalLabel").modal('show');
}

function DomainStatusModify(){
    // 修改domain状态值
    var _action = '';
    var _checkbox_val = GetCheckboxAttrSet("#table_domains", "id");
    var _action = $("#DomainStatusModalLabel").prop('name').trim();
    var __data = {'id_list': _checkbox_val, 'action':_action};

    $.ajax({
        url:"/domains/domain_curd.html?type=status",
        type:"POST",
        data:{'data':JSON.stringify(__data)},
        dataType:"json",
        success:function(callback){
            if (callback['status']  == 200){        // 状态修改成功
                $("#DomainStatusModalLabel").modal('hide');
                DomainPage({'data':{'optype':3}});
            }
        },
        error:function(){

        }
    });
}

function GetCurrentTrId(ths){
    // 获取talbe中当前行input的id值
    var _tag_selectors = $(ths).closest("tr");
    var _id_val = $(_tag_selectors[0]).find("input:first").prop('id');
    return _id_val
}

function GetCurrentTrDomain(ths){
    // 获取talbe中当前行的domain值
    var _tag_selectors = $(ths).closest("tr");
    var _domain_val = $($(_tag_selectors[0]).children()[1]).text();
    return _domain_val
}

function DomainDeleteACK(){
    // domain删除域名弹出确认框
    var _domain_val = GetCurrentTrDomain(this);
    $("h4.modal-title#DomiandDeleteModalLabel").html("删除域名: " + _domain_val);

    var tag_selector = $(this).parent().parent().parent().parent().siblings().filter("input, :first");
    $(tag_selector).children().prop('checked', true);
    $(tag_selector).parents().siblings().find("input[type=checkbox]").prop('checked', false);
    $("#DomiandDeleteModalLabel").modal("show");
}

function DomainDelete(){
    // domain删除域名
    var _action = '';
    var _checkbox_val = GetCheckboxAttrSet("#table_domains", "id")
    var __data = {'id_list': _checkbox_val};
    console.log(__data);
    $.ajax({
        url:"/domains/domain_curd.html?type=d",
        type:"POST",
        data:{'data':JSON.stringify(__data)},
        dataType:"json",
        success:function(callback){
            if (callback['status']  == 200 ){
                $("#DomiandDeleteModalLabel").modal("hide");
                DomainPage({'data':{'optype':3}});
            }
        },
        error:function(){

        }
    });
}

function ShowRecordDataCopyButton(event){
    // 鼠标移动到 record 记录值栏时显示复制按钮,离开时隐藏
    if (event.data.val) {
        $(this).children('a').removeClass('hidden');
    } else {
        $(this).children('a').addClass('hidden');
    }
}

function GetDomainName() {
    // 获取 table_domains 表中，选中的域名的名称
    var _zone = $("#table_domains td input:checked:not([data-check-all])").parent().siblings().filter(":first").text().trim();
    return _zone;
}

$(document).ready(function(){
    //DOM就绪后执行

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

    //添加DNS记录 Placeholder 根据type值变动而改变提示
    //$(".form-horizontal select[name=type]").change(ChangePlaceholder);
    $(".form-horizontal select[name=type]").bind('change', ChangePlaceholder);

    //点击 添加记录 按钮绑定事件
    //$("button[data-toggle=modal]").bind('click', RecordAddACK, ChangePlaceholder);
    $("button[data-toggle=modal]").bind('click', RecordAddACK);

    //添加记录时点击 保存 按键绑定事件
    $(".modal-footer  button[name=_save]").bind('click', RecordAddModify);

    // 选择/取消 所有项
    //$("table tr input[data-check-all]").bind('click', SelectAll);
    $(document).on("click", "table tr input[data-check-all]", SelectAll);

    // DNS记录展示页的操作绑定事件--删除操作按钮 （删除确认）
    //$("table a[action_type=delete]").bind('click', RecordDelteACK);
    $(document).on("click", "table a[action_type=delete]", {'optype': 1}, RecordDelteACK);
    $(document).on("click", ".box-title button[action_type=delete]", {'optype': 2}, RecordDelteACK);

    // 记录删除 确认按钮绑定事件（执行删除）
    //$(".modal-footer button[name=_delete_ok]").bind('click', RecordDel);
    $(document).on("click", ".modal-footer button[name=_delete_ok]", {'optype': 1}, RecordDel);

    // DNS记录展示页的操作绑定事件--状态操作按钮(记录状态操作确认)
    //$("table a[action_type=status]").bind('click', RecordStatusACK);
    $(document).on("click", "table a[action_type=status]", {'optype': 1},  RecordStatusACK);
    $(document).on("click", ".box-title button[action_type=status]", {'optype': 2},  RecordStatusACK);

    // 记录状态操作 确认按钮绑定事件（执行记录状态操作）
    //$("#DNSRecordStatusModalLabel button[name=_modify_status_ok]").bind('click', RedcordStatusModify);
    $(document).on("click", "#DNSRecordStatusModalLabel button[name=_modify_status_ok]", RedcordStatusModify);

    // DNS记录展示页的操作绑定事件--修改操作按钮
    //$("table a[action_type=modify]").bind('click', RecordModifyACK);
    $(document).on("click", "table a[action_type=modify]", RecordModifyACK);

    // 分页导航绑定点击事件
    //$(".pagination a").bind('click', ClickPage);
    $(document).on("click", "#domain_record_box nav .pagination a", {'optype': 1}, ClickPage);       // 点击分页导航器上的分页码, 动态新增元素也生效
    $(document).on("click", "#domain_record_box button[name=jump-page]", {'optype': 2}, ClickPage);       // 点击分页导航器上输入页码直接跳转

    // DNS记录分页导航器选择x条记录/页
    $(document).on("click", "#domain_record_box .dropdown-menu[aria-labelledby='perpage-dropdownMenu'] li a", SelectPerPageNum);

    // 域名解析分页导航器选择x条记录/页
    $(document).on("click", "#domain_resolution_box .dropdown-menu[aria-labelledby='perpage-dropdownMenu'] li a", DomainSelutionSelectPerPageNum);

    // 我的域名分页导航器选择x条记录/页
    $(document).on("click", "#domain_box .dropdown-menu[aria-labelledby='perpage-dropdownMenu'] li a", DomainSelectPerPageNum);

    // 域名解析列表分页导航绑定点击事件
    $(document).on("click", "#domain_resolution_box nav .pagination a", {'optype': 1}, DomainResolutionPage);       // 点击分页导航器上的分页码, 动态新增元素也生效
    $(document).on("click", "#domain_resolution_box button[name=jump-page]", {'optype': 2}, DomainResolutionPage);       // 点击分页导航器上输入页码直接跳转

    // 我的域名 分页导航绑定点击事件
    $(document).on("click", "#domain_box nav .pagination a", {'optype': 1}, DomainPage);       // 点击分页导航器上的分页码, 动态新增元素也生效
    $(document).on("click", "#domain_box button[name=jump-page]", {'optype': 2}, DomainPage);       // 点击分页导航器上输入页码直接跳转

    // DNS记录搜按钮绑搜索事件
    $(document).on("click", "div button[name=dns_record_search_submit]", DnsRecordSearch);

    // 域名解析页 搜索按钮绑定事件
    $(document).on("click", "div button[name=domain_resolution_search_submit]", DomainResolutionSearch);

    // 我的域名页 搜索按钮绑定事件
    $(document).on("click", "div button[name=domain_search_submit]", DomainSearch);

    // 点击 添加域名 弹出添加域名页（添加域名确认操作页面）
    $(document).on("click", "button[name=add_domain]", DoaminAddACK);
    $(document).on("click", "#DomainAddOrModifyModalLabel button[name=_save]", DoaminAdd);

    //域名列表页点击 DNS解析跳转到DNS解析页
    $(document).on("click", "#table_domains tbody a[name=dns_resolution]", DnsResolutionClick);

    //域名列表页点击 DNS解析跳转到DNS解析页
    $(document).on("click", "#table_domains tbody a[name=domain_manager]", DomainMan);

    //点击 新增 域名NS 按钮事件
    $(document).on("click", "#domain_manager button[name=_add_domain_ns]", AddDomainNSHtmlElement);

    // 输入NS主机后，提交到后台
    $(document).on("click", "#domain_manager button[name=_add_domain_submit]", AddDomainNS);

    // 点击 domain ns编辑框后的 删除按钮
    $(document).on("click", "a[name=_domain_ns_edit_del]", DomainNsEditDel);

    // 修改domain状态确认框
    $(document).on("click", "#domain_box li a[action_type=status]", DomainStatusACK);

    // 修改domain状态
    $(document).on("click", "#DomainStatusModalLabel button[name=_modify_status_ok]", DomainStatusModify);

    // 删除domain确认框
    $(document).on("click", "#domain_box li a[action_type=delete]", DomainDeleteACK);

    // 删除domain
    $(document).on("click", "#DomiandDeleteModalLabel button[name=_delete_ok]", DomainDelete);

    // 按下回车键的事件
    EnterdSearch();

    // 上传 导入DNS文件
    $(document).on("click", "button[name=upload_import_dns_file]", UploadImportDNSFile);

    // 确认导入批量导入DNS记录
    $(document).on("click", 'button[name=import_dns_confirm]', ImportDnsRecordACK);

    // 点击 导出DNS解析记录 按钮
    $(document).on("click", 'ul li a[action_type=_export_records]', ExportDnsRecord);

    // 确认 导出DNS解析记录
    $(document).on("click", 'button[name=_export_dns_record_ok]', ExportDnsRecordACK);

    // 鼠标移动到 record 记录值时显示复制按钮,离开时隐藏
    $(document).on('mouseenter', '#table_record_list .record_data', {'val': true}, ShowRecordDataCopyButton)
    $(document).on('mouseleave', '#table_record_list .record_data', {'val': false}, ShowRecordDataCopyButton)
});


