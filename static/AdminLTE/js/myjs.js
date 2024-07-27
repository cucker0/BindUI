/**
 * Created by 0 on 02-27 2016.
 */


/**
 * 字符串格式化
 *
 *  //方式1
 *  var test = '我的{0}是{1}';
 *  var result = test.format('ID','coco56');
 *
 *  //方式2
 *  var test = '我的{description}是{name}';
 *  var result = test.format({description:'ID',name:'coco56'});
 *
 *
 * @returns {String|String|*|string}
 */
String.prototype.format = function () {
    // 字符串格式化
    if (arguments.length === 0) {
        return this;
    }
    for (var s = this, i = 0; i < arguments.length; i++) {
        s = s.replace(new RegExp("\\{" + i + "\\}", "g"), arguments[i]);
    }
    return s;
};


function GetCheckboxValue(selector){
    // 获取目标选择器 input checkbox 选中的值，返回为列表
    var _checkbox_val = [];
    // var _target = selector + ' input:checked[name!="ckSelectAll"]';
    var _target = selector + ' input:checked:not([data-check-all])';
    $(_target).each(function(){
        _checkbox_val.push($(this).val());
    });
    return _checkbox_val;
}


function SelectAll(){
    // 选择/取消所有项
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
    // $.post('/auth/login/', {'data':send_data},
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
    // 用户更改密码
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
            // console.log(callback);
            if (callback['auth_status'] == '1'){  // 登录成功
                location.href = callback['url'];
            }else if(callback['auth_status'] == '0'){  // 登录失败
                var msg = '密码修改失败, 当前密码错误';
                $('#current_password').parent().next().html(msg);
            }
        });
}

function UploadFile(selector, action){
    // 上传文件
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
                // 告诉jQuery不要去处理发送的数据
                processData : false,
                // 告诉jQuery不要去设置Content-Type请求头
                contentType : false,
                // beforeSend: function(){
                //    console.log('正上传中，请稍候');
                // },
                success: function(callback){
                    callback = JSON.parse(callback)['data'];
                    if(callback['status'] == 1){
                        // 上传图片成功
                        location.href = window.location.href;
                    }else if(callback['status'] == 2){
                        $('div[func="msg_error1"]').removeClass('hide');
                        $(selector).parent().prev().attr('placeholder', '选择一个文件');
                    }else{
                        // 上传图片失败
                        $(selector).parent().prev().attr('placeholder', '选择一个文件');
                    }
                },
                error: function(err){
                    console.log(err);
                }
            });
        }
    }else if(action == 2){
        // 取消上传文件
        $('div[func="msg_error1"]').addClass('hide');
        $(selector).val('');
        $(selector).parent().prev().attr('placeholder', '选择一个文件');
    }
}

function UploadImportDNSFile() {
    // 上传导入DNS文件
    var form_data = new FormData();
    var selector = $('input[name=import_dns_file]')
    // var name = $(selector).val();
    form_data.append('file', $(selector)[0].files[0]);
    // form_data.append('name', name);
    var _url = document.URL;
    if ($(selector)[0].files[0]){
        $.ajax({
            url: _url,
            type: 'POST',
            data: form_data,
            // 告诉jQuery不要去处理发送的数据
            processData : false,
            // 告诉jQuery不要去设置Content-Type请求头
            contentType : false,
            // beforeSend: function(){
            //    console.log('正上传中，请稍候');
            // },
            // async: false,
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
    // 取消上传文件
    $('div[func="msg_error1"]').addClass('hide');
    $(selector).val('');
    $(selector).parent().prev().attr('placeholder', '选择一个文件');
}


function ChangeNickname(selector, action){
    // 修改昵称
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

// 禁止双击选中文字
// document.onselectstart=function(){return false;}

function MXShowOrHide(){
    // DNS MX input展示或隐藏
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

var DomainAddOrModifyDefaultValue = {
    zone: "",
    data: "",
    mail: "",
    refresh: 900,
    retry: 900,
    expire: 2592000,
    minimum: 600,
    primary_ns: "",
    comment: ""
};

function ChangeDomainAddModify2Default() {
    // 修改 添加域名/修改域名 模态框恢复默认值
    var action_type = $("#DomainAddOrModifyModalLabel").attr("action_type");
    if(action_type == "add"){  // 恢复默认值
        $("#DomainAddOrModifyModalLabel input[name=zone]").val(DomainAddOrModifyDefaultValue.zone);
        $("#DomainAddOrModifyModalLabel input[name=data]").val(DomainAddOrModifyDefaultValue.data);
        $("#DomainAddOrModifyModalLabel input[name=mail]").val(DomainAddOrModifyDefaultValue.mail);
        $("#DomainAddOrModifyModalLabel input[name=refresh]").val(DomainAddOrModifyDefaultValue.refresh);
        $("#DomainAddOrModifyModalLabel input[name=retry]").val(DomainAddOrModifyDefaultValue.retry);
        $("#DomainAddOrModifyModalLabel input[name=expire]").val(DomainAddOrModifyDefaultValue.expire);
        $("#DomainAddOrModifyModalLabel input[name=minimum]").val(DomainAddOrModifyDefaultValue.minimum);
        $("#DomainAddOrModifyModalLabel input[name=primary_ns]").val(DomainAddOrModifyDefaultValue.primary_ns);
        $("#DomainAddOrModifyModalLabel input[name=comment]").val(DomainAddOrModifyDefaultValue.comment);
    }

}

var _recordPlaceholder = {
    host: {
        mx: "通常填写@，不填写默认保存为@",
        srv: "填写格式为：服务.协议（如_ldap._tcp）",
        ptr: "填写IP主机位数字（如反向解析IP 192.168.1.11，则填写11）；IPv6（2a03:2880:f11c:8083:face:b00c:0:25de）填写e.d.5.2.0.0.0.0.c.0.0.b.e.c.a.f",
        soa: "填写@，不填写默认保存为@",
        uri: "填写子域名（如www），格式：_service._proto，如：_ftp._tcp",
        common: "填写子域名（如www），*表示泛域名，不填写默认保存为@",
    },
    data: {
        cname: "填写一个域名，例如：www.dns.com.",
        mx: "填写邮件服务器地址，如：mx2.dns.com.",
        txt: "填写文本（>255个字符将自动分割成多个字符串），如：v=spf1 include:spf.mail.qq.com -all",
        ns: "填写DNS域名，例如：ns1.google.com.",
        aaaa: "填写一个IPv6地址，例如：ff06:0:0:0:0:0:0:c3",
        srv: "格式为：优先级 权重 端口 主机名，例如：5 0 5269 example.dns.com.",
        ptr: "填写对应的正向解析域名，例如：www.dns.com.",
        soa: "填写一个域名，例如：ns1.dns.com.",
        caa: '填写tag-value 标签-值 对,如：0 issue "ca.abc.com"，参考https://sslmate.com/caa/',
        uri: '格式：priority weight "target"，如：10 1 "ftp://ftp1.example.com/public"',
        explicit_url: "填写要跳转到的网址，如：http://www.qq.com",
        implicit_url: "填写要跳转到的网址，如：https://www.qq.com",
        default: "填写一个IPv4地址，例如：8.8.8.8"
    }
};

function ChangePlaceholder(){
    var action_type = $("#RecordAddOrModifyModalLabel").attr("action_type");
    if(action_type == "add"){       // 添加记录，清空host，data值
        $("#RecordAddOrModifyModalLabel .form-horizontal input[name=host]").val("");
        $("#RecordAddOrModifyModalLabel .form-horizontal input[name=data]").val("");
        $("#RecordAddOrModifyModalLabel .form-horizontal input[name=comment]").val("");
    }

    // 添加DNS记录选择记录类型时，自动调整相应的Placeholder提示内容
    var type_val = $(".form-horizontal select[name=type]").val();
    MXShowOrHide();
    RedirectCodeShowOrHide();

    switch(type_val){
        case 'CNAME':

            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.common);
            $(".form-horizontal input[name=data]").prop("placeholder", );
            break;
        case 'MX':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.mx);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.mx);
            break;
        case 'TXT':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.common);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.txt);
            // $(".form-horizontal input[name=mx]").parent().parent().hide();
            break;
        case 'NS':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.common);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.ns);
            break;
        case 'AAAA':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.common);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.aaaa);
            break;
        case 'SRV':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.srv);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.srv);
            break;
        case 'PTR':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.ptr);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.ptr);
            break;
        case 'SOA':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.soa);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.soa);
            break;
        case 'CAA':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.common);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.caa);
            break;
        case 'URI':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.uri);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.uri);
            break;
        case 'EXPLICIT_URL':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.common);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.explicit_url);
            break;
        case 'IMPLICIT_URL':
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.common);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.implicit_url);
            break;
        default:
            $(".form-horizontal input[name=host]").prop("placeholder", _recordPlaceholder.host.common);
            $(".form-horizontal input[name=data]").prop("placeholder", _recordPlaceholder.data.default);
            // $(".form-horizontal input[name=mx]").parent().parent().hide();
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


function ImportRecordACK(){
    // 批量导入DNS记录
    var record_set = [];
    var _zone_id = $("p[name=import_dns_domain]").attr("zone_id").trim();
    _zone_id = parseInt(_zone_id);
    $("#table_import_dns tbody tr").each(function(){
        var _record = {};
        _record['host'] = $($(this).find('td')).children()[0].value.trim();
        _record['type'] = $($(this).find('td')).children()[1].value.trim();
        _record['data'] = $($(this).find('td')).children()[2].value.trim();
        _record['ttl'] = $($(this).find('td')).children()[4].value.trim();
        _record['resolution_line'] = $($(this).find('td')).children()[5].value.trim();
        _record['comment'] = $($(this).find('td')).children()[6].value.trim();
        if (_record.type === 'MX') {
            _record['mx_priority'] = $($(this).find('td')).children()[3].value.trim();
        }
        _record['zone_id'] = _zone_id;
        record_set.push(_record);
    });
    // console.log(record_set);
    if(record_set.length > 0){
       $.ajax({
            url: "/dns/add.html",
            type: "POST",        //请求类型
            data: {'data': JSON.stringify(record_set)},
            dataType: "json",
            success: function (callback) {
                // 当向服务端发起的请求执行成功完成后，自动调用
                if (callback['status'] == 200){  // 刷新当前页面,status=500 添加记录失败。
                    $("#table_import_dns").html('');
                    console.log("恭喜，导入DSN记录成功！");
                    var url = "/dns/" + _zone_id;
                    location.href = url;
                    ClickPage( { 'data':{'optype':5} } );  // 分页器中查看最后一页
                }
            },
            error: function () {
                // 当请求错误之后，自动调用
                $("#table_import_dns").html('');
            }
        });
    }
}

function ExportRecord(){
    // 点击导出DNS解析记录
    $('#ExportRecordModalLabel').modal('show');
    var _zone_name = $($(this).parent().parent().parent().parent().siblings()[1]).html();
    var _zone_id = $($(this).parent().parent().parent().parent().siblings()[0]).find("input").attr("id");
    // var _modal_title = $("#ExportRecordModalLabel h4").html();
    var _modal_title = '导出DNS解析记录';
    _modal_title = _zone_name + ' ' +  _modal_title;

    $("#ExportRecordModalLabel h4").html(_modal_title);
    $("#ExportRecordModalLabel h4").attr('zone_name', _zone_name);
    $("#ExportRecordModalLabel h4").attr('zone_id', _zone_id);



}

function ExportRecordACK(){
    // 确认导出DNS解析记录
    var _record_format_type = $("select[name=record_format_type]")[0].value.trim();
    // var _zone_name = $("#ExportRecordModalLabel h4").attr('zone_name');
    var _zone_id = $("#ExportRecordModalLabel h4").attr('zone_id');
    var __data = {record_format_type: _record_format_type, zone_id:_zone_id}

    var url = "/domains/_export_dns.html?data=" + JSON.stringify(__data);

    window.location.href = url;  // 下载文件
    $('#ExportRecordModalLabel').modal('hide');
    $("select[name=record_format_type]").val('0')
    $("#ExportRecordModalLabel h4").attr('zone_name', '');
    $("#ExportRecordModalLabel h4").attr('zone_id', '');

    // $.ajax({
    //     url: "/domains/_export_dns.html",
    //     type: "POST",        //请求类型
    //     data: {},
    //     //async : false,
    //     dataType: "json",
    //     //beforeSend:function(XMLHttpRequest){
    //     //    // 请求前执行
    //     //},
    //     success: function (callback) {
    //         //当向服务端发起的请求执行成功完成后，自动调用
    //         if(callback['status'] == 200){
    //             $('#ExportRecordModalLabel').modal('hide');
    //             $("select[name=record_format_type]").val('0')
    //             $("#ExportRecordModalLabel h4").attr('zone_name', '');
    //             $("#ExportRecordModalLabel h4").attr('zone_id', '');
    //             window.location.href = url;     //下载文件
    //         }
    //     },
    //     error: function () {
    //         //当请求错误之后，自动调用
    //     }
    // });
}

function  GetCheckboxAttrSet(selector, attr){
    // 获取checkbox 属性集合值, 返回为列表
    var _set = [];
    var _tag_selector =  selector + " input:checked:not([data-check-all])";
    $(_tag_selector).each(function () {
        _set.push($(this).prop(attr));
    });
    return _set;
}


function RecordAddACK(){
    // 添加DNS记录确认操作页面
    $("#RecordAddOrModifyModalLabel .modal-title").html("添加记录");         //修改modal标题内容
    $("#RecordAddOrModifyModalLabel").attr("action_type", "add");        //修改 action_type值

    // 每次点击 添加记录 重置记录类型,并改变Placeholder值
    $("#RecordAddOrModifyModalLabel .form-horizontal input[name=mx]").parent().parent().hide();
    // $("#RecordAddOrModifyModalLabel .form-horizontal input[name=host]").val('');
    $("#RecordAddOrModifyModalLabel .form-horizontal select[name=resolution_line]").val('0');
    // $("#RecordAddOrModifyModalLabel .form-horizontal input[name=data]").val('');
    $("#RecordAddOrModifyModalLabel .form-horizontal select[name=ttl]").val('600');
    // $("#RecordAddOrModifyModalLabel .form-horizontal input[name=comment]").val('');
    var _domain_name = $("div[zone_name]").text().trim();
    if (_domain_name.endsWith('in-addr.arpa')
        || _domain_name.endsWith('in-addr.arpa.')
        || _domain_name.endsWith('ip6.arpa.')
        || _domain_name.endsWith('ip6.arpa')
    ) {
        $(".form-horizontal select[name=type]").val('PTR');
        $(".form-horizontal input[name=host]").attr("placeholder", _recordPlaceholder.host.ptr);
        $(".form-horizontal input[name=data]").attr("placeholder", _recordPlaceholder.data.ptr);
    }else{
        $(".form-horizontal select[name=type]").val('A');
        // $(".form-horizontal input[name=host]").attr("placeholder", "填写子域名（如www），不填写默认保存为@");
        // $(".form-horizontal input[name=data]").attr("palceholder", "填写一个IPv4地址，例如：8.8.8.8");
    }
    ChangePlaceholder();
}

function RecordModifyACK(){
    // DNS记录修改确认操作页面
    $("#RecordAddOrModifyModalLabel .modal-title").html("修改记录");     //修改modal标题内容
    $("#RecordAddOrModifyModalLabel").attr("action_type", "modify");        //修改 action_type值

    $('#RecordAddOrModifyModalLabel').modal('show');
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
    $("#RecordAddOrModifyModalLabel .modal-title").prop("id", _id);

    MXShowOrHide();
    RedirectCodeShowOrHide();
}

function RecordAddModify(){
    // 添加记录/修改记录 点击 保存按键
    var _type = $(".modal-body select[name=type]").val().trim();
    var _host = $(".modal-body input[name=host]").val().trim();
    var _resolution_line = $(".modal-body select[name=resolution_line]").val().trim();
    var _data = $(".modal-body input[name=data]").val().trim();
    var _mx = $(".modal-body input[name=mx]").val().trim();
    var _ttl = $(".modal-body select[name=ttl]").val().trim();
    var _zone_id = $("#table_record_list").attr("zone_id").trim();
    var _comment = $(".modal-body input[name=comment]").val().trim();
    var _redirect_code = $(".modal-body select[name=redirect_code]").val().trim();
    var __data = {
        type: _type,
        host: _host,
        resolution_line: _resolution_line,
        data: _data,
        mx_priority: _mx,
        ttl: _ttl,
        comment: _comment,
        zone_id: _zone_id
    };

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
    var action_type = $("#RecordAddOrModifyModalLabel").attr("action_type");
    if (action_type == "add"){  //添加记录
        var record_set = [];
        record_set.push(__data);
        $.ajax({
            url: "/dns/add.html",
            type: "POST",        //请求类型
            data: {'data': JSON.stringify(record_set)},
            dataType: "json",
            success: function (callback) {
                // 当向服务端发起的请求执行成功完成后，自动调用
                if (callback['status'] == 200){  // 刷新当前页面,status=500 添加记录失败。
                    $("#RecordAddOrModifyModalLabel").modal('hide');
                    ClickPage( { 'data':{'optype':5} } );  // 分页器中查看最后一页
                    //location.reload(true);
                }
            },
            error: function () {
                // 当请求错误之后，自动调用
            }
        });
    } else if (action_type == "modify"){        //修改记录
        var _id = $("#RecordAddOrModifyModalLabel .modal-title").prop("id");
        $("#RecordAddOrModifyModalLabel .modal-title").removeProp("id");
        __data['id'] = _id;
        // var history_search_key = $("#table_record_list").attr("history_search_key");
        // var _history_search_key = $("#table_record_list").attr("history_search_key").trim();
        $.ajax({
            url: "/dns/mod.html?type=main",
            type: "POST",        //请求类型
            data: {'data': JSON.stringify(__data)},
            dataType: "json",
            success: function (callback) {
                //当向服务端发起的请求执行成功完成后，自动调用
                if (callback['status'] == 200){ //刷新当前页面,status=500 添加记录失败。
                    //location.reload(true);
                    $("#RecordAddOrModifyModalLabel").modal('hide');
                    ClickPage( { 'data':{'optype':3} } );
                    // if(_history_search_key == ""){
                    //    ClickPage( { 'data':{'optype':3} } );
                    // }else{
                    //    ClickPage( { 'data':{'optype':6} } );
                    // }

                    ClearRecordAddModModal();
                }
            },
            error: function () {
                // 当请求错误之后，自动调用
            }
        });
    }


}

function RecordDelteACK(event){
    // 记录删除确认，显示删除记录模态对话框(删除确认)
    if(event.data.optype == 1){ // 单条记录操作
        var tag_selector = $(this).parent().siblings().filter("input, :first");  // <td>...</td>
        tag_selector.children().prop("checked", true);  // 当前行打勾
        tag_selector.parent().siblings().find('input').removeAttr("checked");  // 取消其他行的勾
        $(this).parent().parent().parent().prev().find("input").removeAttr("checked");  // 取消 selectAll 勾
        $("#RecordDeleteModalLabel").prop("multiple", 0);  // 标识为非多条操作
    }else if (event.data.optype == 2){
        $("#RecordDeleteModalLabel").prop("multiple", 1);  // 标识为多条操作
    }

    $('#RecordDeleteModalLabel').modal('show');
    var _tip = "<b>{0}</b>.{1} &emsp;[{2}, {3}] &emsp;记录删除？";
    var _rr = GetCheckedRecord();
    var tip = "确定删除所选择的解析记录吗？";

    if (_rr.status) {
        tip = _tip.format(_rr.host, _rr.zone, _rr.type, _rr.resolution_line);
    }
    $("#RecordDeleteModalLabel td .tit").html(tip);

}

function RecordDel(){
    // 删除DNS记录（执行删除）
    var _checkbox_val = [];
    var multiple = $("#RecordDeleteModalLabel").prop("multiple");
    if(multiple == 0){  // 单条操作
        var select_id = $("#table_record_list tbody input:checked").prop('id');
        _checkbox_val.push(select_id);
    } else {  // 多条操作
        // $("#table_record_list input:checked:not([data-check-all])").each(function () {
        //    _checkbox_val.push($(this).attr("id"));
        // });
        _checkbox_val = GetCheckboxAttrSet("#table_record_list", "id")
    }

    $.ajax({
        url: "/dns/del.html",
        type: "POST",  // 请求类型
        data: {'data': JSON.stringify(_checkbox_val)},
        dataType: "json",
        success: function (callback) {
            //当向服务端发起的请求执行成功完成后，自动调用
            if (callback['status'] == 200) {
                // location.reload(true);  // 刷新当前页面,status=500 添加记录失败。
                $("#RecordDeleteModalLabel").modal('hide');
                ClickPage({'data':{'optype':3}});
            }
        },
        error: function () {
            // 当请求错误之后，自动调用
        }
    });
}

function RecordStatusACK(event){
    // DNS记录状态修改确认操作页面
    if(event.data.optype == 1){  // 单条操作
        var tag_selector = $(this).parent().siblings().filter("input, :first");  // <td>...</td>
        tag_selector.children().prop("checked", true);  // 当前行打勾
        tag_selector.parent().siblings().find('input').removeAttr("checked");  // 取消其他行的勾
        $(this).parent().parent().parent().prev().find("input").removeAttr("checked");  // 取消 selectAll 勾
        $("#RecordStatusModalLabel").prop("multiple", 0);
    } else if(event.data.optype == 2){  // 多条操作
        $("#RecordStatusModalLabel").prop("multiple", 1);
    }
    var _status = $(this).prop('name');
    $("#RecordStatusModalLabel").prop('name', _status);  // 在DNS记录状态操作模态框中标识 DNS记录状态操作动态类型
    var _tip = "<b>{0}</b>.{1} &emsp;[{2}, {3}] &emsp;记录{4}？";
    var _rr = GetCheckedRecord();
    var tip = "暂停记录吗？";
    if (_status == '_turnOff'){

        if (_rr.status) {
            tip = _tip.format(_rr.host, _rr.zone, _rr.type, _rr.resolution_line, "暂停");
        }
        $("#RecordStatusModalLabel td .info").html(tip);

    } else if(_status == '_turnOn'){
        tip = "开启记录吗？";
        if (_rr.status) {
            tip = _tip.format(_rr.host, _rr.zone, _rr.type, _rr.resolution_line, "开启");
        }
        $("#RecordStatusModalLabel td .info").html(tip);
    }
    $('#RecordStatusModalLabel').modal('show');
}

function RedcordStatusModify(){
    // 修改记录状态
    var _checkbox_val = [];
    var _action = '';
    var multiple = $("#RecordStatusModalLabel").prop("multiple");
    // var _history_search_key = $("#table_record_list").attr("history_search_key").trim();
    if(multiple == 0){
        var select_id = $("#table_record_list tbody input:checked").prop('id');
        _checkbox_val.push(select_id);
        // _action = $("#table_record_list tbody tr").has(":checked").find('a[action_type=status]').attr('name');
        _action = $(this).prop('name');
    }else if(multiple == 1){
        _checkbox_val = GetCheckboxAttrSet("#table_record_list", 'id');
        _action = $("#RecordStatusModalLabel").prop('name');
    }
    _checkbox_val = GetCheckboxAttrSet("#table_record_list", 'id');
    _action = $("#RecordStatusModalLabel").prop('name');


    var data = {'action':_action, 'id_list':_checkbox_val};

    $.ajax({
        url:"/dns/mod.html?type=status",
        type:"POST",
        data:{'data':JSON.stringify(data)},
        dataType:"json",
        success:function(callback){
            if (callback['status']  == 200){  // 状态修改成功
                // location.reload(true);
                $("#RecordStatusModalLabel").modal('hide');
                // if(_history_search_key == ""){
                //    ClickPage({'data':{'optype':3}});
                // }else {
                //    ClickPage({'data':{'optype':6}});
                // }
                ClickPage({'data':{'optype':3}});

            }
        },
        error:function(){

        }
    });
}


function ClickPage(event){
    // 点击分页
    // event ==> { 'data': {'optype': 1} }
    // event.data 为含操作类型字典 ==> { 'optype': 1 }
    var page_num = 1;
    var active_page_num = parseInt( $(".pagination li.active a").text().trim() ) || 1;
    var _action = 'pagination';     // 点击分页(搜索还是点击分页)
    var _other = {};  // 其他参数
    // var _history_search_key = $("#table_record_list").attr("history_search_key").trim();
    var _search_key = $("input[name=dns_record_search]").val().trim();
    // _other['history_search_key'] = _history_search_key;
    if (event.data.optype == 1){   // 点击分页导航器上的分页码

        if ( typeof($(this).attr("aria-label")) != "undefined" ){
            if ($(this).parent().hasClass("disabled")){  // 上一页、下一页若为 disabled 直接退出
                return 400;
            }

            var PN = $(this).attr("aria-label");
            if (PN == "Previous"){  // 查看上一页
                page_num = active_page_num - 1;
            } else if (PN == "Next"){  // 查看下一页
                page_num = active_page_num + 1;
            }
        } else{
            page_num = $(this).text().trim();
            if (!parseInt(page_num)){
                console.log("page number is error!");
                return 400;
            }
        }


    }else if (event.data.optype == 2){  // 点击分页导航器上输入页码直接跳转
        page_num = $("#input_page").val().trim();
        $(this).prev().val('');
        if (!parseInt(page_num)){
            console.log("page number is error!");
            return 400;
        }
    }else if(event.data.optype == 3){  // 刷新当前分页（如修改了记录状态后刷新回本分页）
        page_num = active_page_num;
    }else if(event.data.optype == 4){  // 搜索record记录
        _action = 'search';  // 搜索分页(搜索还是点击分页)
        //_other = {'search_key':event.data.search_key};
    }else if(event.data.optype == 5){  // 查看最后一页
        page_num = 0;
    }else if(event.data.optype == 6){  // 修改搜索的record记录及其状态
        _action = 'search';
        // _other = {'search_key':_history_search_key};
    }

    var perpage_num = $("#perpage-dropdownMenu").attr('value') || 10;
    var active_page = $(".pagination .active").text() || 1;

    _other = {'search_key':_search_key};
    if (page_num != active_page || (event.data.optype != 1) || (event.data.optype != 2)){
        var _zone_id = $("#table_record_list").attr("zone_id").trim();

        var __data = {'action':_action, 'page':page_num, 'zone_id':_zone_id, 'perpage_num':perpage_num, 'other':_other}
        // console.log(__data);
        var html = $.ajax({
            url: "/dns/rlist_page.html",
            type:"POST",
            data:{'data':JSON.stringify(__data)},
            dataType:"json",
            async: false,
        }).responseText;
        $("#domain_record_box").html(html);
        // $(".pagination a").bind('click', ClickPage)
    }

}

function DomainResolutionPage(event){
    // 域名解析列表分页
    // event ==> { 'data': {'optype': 1} }
    // event.data 为含操作类型字典 ==> { 'optype': 1 }
    var page_num = 1;
    var active_page_num = parseInt( $(".pagination li.active a").text().trim() ) || 1;
    var _action = 'pagination';  // 点击分页(搜索还是点击分页)
    var _other = {};  // 其他参数

    if (event.data.optype == 1){  // 点击分页导航器上的分页码

        if ( typeof($(this).attr("aria-label")) != "undefined" ){
            if ($(this).parent().hasClass("disabled")){  // 上一页、下一页若为 disabled 直接退出
                return 400;
            }

            var PN = $(this).attr("aria-label");
            if (PN == "Previous"){  // 查看上一页
                page_num = active_page_num - 1;
            } else if (PN == "Next"){  // 查看下一页
                page_num = active_page_num + 1;
            }
        } else{
            page_num = $(this).text().trim();
            if (!parseInt(page_num)){
                console.log("page number is error!");
                return 400;
            }
        }


    }else if (event.data.optype == 2){  // 点击分页导航器上输入页码直接跳转
        page_num = $("#input_page").val().trim();
        $(this).prev().val('');
        if (!parseInt(page_num)){
            console.log("page number is error!");
            return 400;
        }
    }else if(event.data.optype == 3){  // 刷新当前分页（如修改了记录状态后刷新回本分页）
        page_num = active_page_num;
    }else if(event.data.optype == 4){  // 搜索record记录
        _action = 'search';  // 搜索分页(搜索还是点击分页)
        _other = {'search_key':event.data.search_key};
    }else if(event.data.optype == 5){  // 查看最后一页
        page_num = 0;
    }

    var perpage_num = $("#perpage-dropdownMenu").attr('value') || 10;
    var active_page = $(".pagination .active").text() || 1;

    if (page_num != active_page || (event.data.optype != 1) || (event.data.optype != 2)){

        var __data = {'action':_action, 'page':page_num, 'perpage_num':perpage_num, 'other':_other};
        // console.log(__data);
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
    var _action = 'pagination';  // 点击分页(搜索还是点击分页)
    var _other = {};  // 其他参数

    if (event.data.optype == 1){  // 点击分页导航器上的分页码

        if ( typeof($(this).attr("aria-label")) != "undefined" ){
            if ($(this).parent().hasClass("disabled")){  // 上一页、下一页若为 disabled 直接退出
                return 400;
            }

            var PN = $(this).attr("aria-label");
            if (PN == "Previous"){  // 查看上一页
                page_num = active_page_num - 1;
            } else if (PN == "Next"){  // 查看下一页
                page_num = active_page_num + 1;
            }
        } else{
            page_num = $(this).text().trim();
            if (!parseInt(page_num)){
                console.log("page number is error!");
                return 400;
            }
        }


    }else if (event.data.optype == 2){  // 点击分页导航器上输入页码直接跳转
        page_num = $("#input_page").val().trim();
        $(this).prev().val('');
        if (!parseInt(page_num)){
            console.log("page number is error!");
            return 400;
        }
    }else if(event.data.optype == 3){  // 刷新当前分页（如修改了记录状态后刷新回本分页）
        page_num = active_page_num;
    }else if(event.data.optype == 4){  // 搜索record记录
        _action = 'search';     // 搜索分页(搜索还是点击分页)
        _other = {'search_key':event.data.search_key};
    }else if(event.data.optype == 5){  // 查看最后一页
        page_num = 0;
    }

    var perpage_num = $("#perpage-dropdownMenu").attr('value') || 10;
    var active_page = $(".pagination .active").text() || 1;

    if (page_num != active_page || (event.data.optype != 1) || (event.data.optype != 2)){

        var __data = {'action':_action, 'page':page_num, 'perpage_num':perpage_num, 'other':_other};
        // console.log(__data);
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
    // 选择x条记录/页
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

function RecordSearch(){
    // DNS记录搜索
    var _search_key = $("input[name=dns_record_search]").val().trim();
    // $("input[name=dns_record_search]").val('');

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
            // if (document.activeElement.name == 'dns_record_search'){
            //    RecordSearch();
            // } else if (document.activeElement.name == 'domain_resolution_search'){
            //    DomainResolutionSearch();
            // }
            switch (document.activeElement.name) {
                case 'dns_record_search':
                    RecordSearch();
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
    DisalbeDomainZoneEdit(false);

    ChangeDomainAddModify2Default();
}

function DoaminModifyACK(){
    // 修改域名确认操作页面
    var _domain_val = GetCurrentTrDomain(this);
    $("#DomainAddOrModifyModalLabel").modal("show");
    $("#DomainAddOrModifyModalLabel .modal-title").html("修改域名：<b>" + _domain_val + "</b>" );  // 修改modal标题内容
    $("#DomainAddOrModifyModalLabel").attr("action_type", "modify");  // 修改 action_type值

    var tag_selector = $(this).parent().parent().parent().parent().siblings().filter("input, :first");
    $(tag_selector).children().prop('checked', true);
    $(tag_selector).parents().siblings().find("input[type=checkbox]").prop('checked', false);

    // 通过 域名id 获取域名信息
    $.ajax({
        url:"/domains/api/get_domain/" + GetCheckedDomainId(),
        type:"GET",
        // data:{'data':JSON.stringify({})},
        dataType:"json",
        success:function(callback){
            if (!callback) {
                return;
            }
            $("#DomainAddOrModifyModalLabel input[name=zone_name]").val(GetCheckedDomainName);
            $("#DomainAddOrModifyModalLabel input[name=data]").val(callback['data']);
            $("#DomainAddOrModifyModalLabel input[name=mail]").val(callback['mail']);
            $("#DomainAddOrModifyModalLabel input[name=refresh]").val(callback['refresh']);
            $("#DomainAddOrModifyModalLabel input[name=retry]").val(callback['retry']);
            $("#DomainAddOrModifyModalLabel input[name=expire]").val(callback['expire']);
            $("#DomainAddOrModifyModalLabel input[name=minimum]").val(callback['minimum']);
            $("#DomainAddOrModifyModalLabel input[name=primary_ns]").val(callback['primary_ns']);
            $("#DomainAddOrModifyModalLabel input[name=comment]").val(callback['comment']);

            DisalbeDomainZoneEdit(true);
        },
        error:function(){

        }
    });
}

function DoaminAddModify(){
    // 添加域名/修改域名 点击 保存按钮

    var _zone_name = $("#DomainAddOrModifyModalLabel input[name=zone_name]").val().trim();
    var _data = $("#DomainAddOrModifyModalLabel input[name=data]").val().trim();
    var _mail = $("#DomainAddOrModifyModalLabel input[name=mail]").val().trim();
    var _refresh = $("#DomainAddOrModifyModalLabel input[name=refresh]").val().trim();
    var _retry = $("#DomainAddOrModifyModalLabel input[name=retry]").val().trim();
    var _expire = $("#DomainAddOrModifyModalLabel input[name=expire]").val().trim();
    var _minimum = $("#DomainAddOrModifyModalLabel input[name=minimum]").val().trim();
    var _primary_ns = $("#DomainAddOrModifyModalLabel input[name=primary_ns]").val().trim();
    var _comment = $("#DomainAddOrModifyModalLabel input[name=comment]").val().trim();

    var action_type = $("#DomainAddOrModifyModalLabel").attr("action_type").trim();
    var __data;
    if (action_type === "add") {  // 添加域名
        __data = {
            rr: {
                data: _data,
                mail: _mail,
                refresh: _refresh,
                retry: _retry,
                expire: _expire,
                minimum: _minimum,
                primary_ns: _primary_ns,
                comment: _comment
            },
            zone_name: _zone_name
        };

        $.ajax({
            url:"/domains/domain_curd.html?type=c",
            type:"POST",
            data:{'data':JSON.stringify(__data)},
            dataType:"json",
            success:function(callback){
                if (callback['status']  == 200){  // 状态修改成功
                    $("#DomainAddOrModifyModalLabel").modal('hide');
                    location.reload(true);
                }
            },
            error:function(){

            }
        });
    } else if (action_type === "modify") {  // 修改域名（除 status 属性以外的属性）
        __data = {
            rr: {
                data: _data,
                mail: _mail,
                refresh: _refresh,
                retry: _retry,
                expire: _expire,
                minimum: _minimum,
                primary_ns: _primary_ns,
                comment: _comment
            },
            zone_id: GetCheckedDomainId()
        };

        $.ajax({
            url:"/domains/domain_curd.html?type=m",
            type:"POST",
            data:{'data':JSON.stringify(__data)},
            dataType:"json",
            success:function(callback){
                if (callback['status']  == 200){  // 状态修改成功
                    $("#DomainAddOrModifyModalLabel").modal('hide');
                    DisalbeDomainZoneEdit(false);
                    location.reload(true);
                }
            },
            error:function(){

            }
        });
    }

}

function DnsResolutionClick(){
    // 域名列表页点击 DNS解析跳转到DNS解析页
    var zone_id = $(this).parent().siblings().first().find("input").prop("id").trim();
    var url = "/dns/" + zone_id;
    location.href = url;
}


function DomainMan(){
    // 域名列表页点击 管理跳转到DNS管理页
    var zone_id = $(this).parent().siblings().first().find("input").prop("id").trim();
    var url = "/domains/" + zone_id + "/info";
    location.href = url;
}

function AddDomainNSHtmlElement(){
    // 点击 新增 域名NS 按钮添加输入框
    var element = '\
        <ul class="row"> \
            <li class="col-md-2"> </li> \
            <li class="col-md-5"><input name="ns" type="text" class="col-md-12" placeholder="NS主机，如：ns1.bindui.com."></li> \
            <a href="javascript:;" name="_domain_ns_edit_del">删除</a> \
        </ul>';
    $(this).parent().parent().parent().append(element);
}


function AddDomainNS(){
    // 新建domain ns记录，输入NS主机名后，提交到后台
    var _ns_list = [];
    var ele_ul = $(this).parent().parent().siblings();
    var _zone_name = $(ele_ul).find("li[zone_name]").attr('zone_name').trim();
    var _zone_id = $(ele_ul).find("li[zone_id]").attr('zone_id').trim();
    _zone_id = parseInt(_zone_id);
    $(ele_ul).find("input[name=ns]").each(function (i) {
        var _ns = $(this).val().trim();
        if ( !(_ns == '' || _ns == undefined) ){
            _ns_list.push(_ns);
        }
    });
    var __data = {zone_id:_zone_id, ns_list:_ns_list};
    $.ajax({
        url:"/domains/domain_curd.html?type=ns",
        type: "POST",
        data: {data: JSON.stringify(__data)},
        dataType:"json",
        success:function(callback){
            if (callback['status']  == 200){  // 状态修改成功
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
    $("#DomainStatusModalLabel").prop('name', _status);  // 在DNS记录状态操作模态框中标识 DNS记录状态操作动作类型
    if (_status == '_turnOff'){
        $("#DomainStatusModalLabel td .info").html('<b>' + GetCheckedDomainName() + '</b> 域名暂停？');
    } else if(_status == '_turnOn'){
        $("#DomainStatusModalLabel td .info").html('<b>' + GetCheckedDomainName() + '</b> 域名开启？');
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
            if (callback['status']  == 200){  // 状态修改成功
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
    $("h4.modal-title#DomiandDeleteModalLabel").html("删除域名：<b>" + _domain_val + "</b>");

    var tag_selector = $(this).parent().parent().parent().parent().siblings().filter("input, :first");
    $(tag_selector).children().prop('checked', true);
    $(tag_selector).parents().siblings().find("input[type=checkbox]").prop('checked', false);
    $("#DomiandDeleteModalLabel").modal("show");
}

function DomainDelete(){
    // domain删除域名
    var _action = '';
    var _checkbox_val = GetCheckboxAttrSet("#table_domains", "id");
    var __data = {'id_list': _checkbox_val};
    // console.log(__data);
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

function GetCheckedDomainName() {
    // 获取 table_domains 表中，选中的域名的名称
    var _zone_name = $("#table_domains td input:checked:not([data-check-all])").parent().siblings().filter(":first").text().trim();
    // var _zone = $("#table_domains td input:checked:not([data-check-all])").parent().siblings().filter("td[name=zone]").text().trim();
    return _zone_name;
}

function GetCheckedDomainId() {
    // 获取 table_domains 表中，选中的域名的id
    var _id = $("#table_domains td input:checked:not([data-check-all])").prop("id").trim();
    return parseInt(_id);
}

/**
 * 修改域名时，zone(域名) 设置不可编辑/可编辑
 *
 * @param option 是否可编辑，true: 不可编辑，false: 可编辑
 * @constructor
 */
function DisalbeDomainZoneEdit(option=true) {
    if (option) {
        $("#DomainAddOrModifyModalLabel input[name=zone_name]").prop("disabled", true);
    } else {
        $("#DomainAddOrModifyModalLabel input[name=zone_name]").prop("disabled", false);
    }
}

function GetCheckedRecord() {
    // 当 #table_record_list 列表中只选中了一条记录时，返回该条记录的信息。数据格式：{status: status, data: {host:host, zone:zone, ...}}
    var _d = {status: false};
    var _checkbox_id_list = GetCheckboxAttrSet("#table_record_list", "id");
    if (_checkbox_id_list.length !== 1) {
        return _d;
    }
    _d.status = true;

    var _tds = $("#table_record_list td input:checked:not([data-check-all])").parent().siblings();
    _d.host = _tds.find("span").first().text().trim();
    _d.zone =$("div[zone_name]").text().trim();
    _d.type = $(_tds[1]).text().trim();
    _d.resolution_line = $(_tds[2]).text().trim();
    return _d;
}

/**
 * 导入DNS解析记录时，mx_priority input框是否可输入
 *
 * @constructor
 */
function MxPriorityInputAutoDisable() {
    console.log($(this).val());
    var _type = $(this).val();
    var mx_priority_input_ele = $(this).parent().siblings().find("input[name=mx_priority]");
    console.log(mx_priority_input_ele[0]);
    if (_type === 'MX') {
        mx_priority_input_ele.prop('disabled', false);
    } else {
        mx_priority_input_ele.val('');
        mx_priority_input_ele.prop('disabled', true);
    }
}

function ClearPreviousInput() {
    // input 框内的 x，清空该 input 输入的内容
    $(this).prev("input").val('');
}

$(document).ready(function(){
    // DOM就绪后执行

    // 点击 上传 按钮，代替点击 上传头像的input
    $('span[func="select_upload_file"]').bind('click', function(){
        $(this).next().filter('input').click();
    });

    // 上传头像文件，前面框提示PATH
    $('#startUploadBtn').change(function(){
            var file_path = $(this).val();
            $(this).parent().prev().attr('placeholder', file_path);
        }
    );

    // 添加DNS记录 Placeholder 根据type值变动而改变提示
    // $(".form-horizontal select[name=type]").change(ChangePlaceholder);
    $(".form-horizontal select[name=type]").bind('change', ChangePlaceholder);

    // 点击 添加记录 按钮绑定事件
    // $("button[data-toggle=modal]").bind('click', RecordAddACK, ChangePlaceholder);
    $("button[data-toggle=modal]").bind('click', RecordAddACK);

    // 添加记录时点击 保存 按键绑定事件
    $("#RecordAddOrModifyModalLabel button[name=_save]").bind('click', RecordAddModify);

    // 选择/取消 所有项
    // $("table tr input[data-check-all]").bind('click', SelectAll);
    $(document).on("click", "table tr input[data-check-all]", SelectAll);

    // DNS记录展示页的操作绑定事件--删除操作按钮 （删除确认）
    // $("table a[action_type=delete]").bind('click', RecordDelteACK);
    $(document).on("click", "table a[action_type=delete]", {'optype': 1}, RecordDelteACK);
    $(document).on("click", ".box-title button[action_type=delete]", {'optype': 2}, RecordDelteACK);

    // 记录删除 确认按钮绑定事件（执行删除）
    // $(".modal-footer button[name=_delete_ok]").bind('click', RecordDel);
    $(document).on("click", "#RecordDeleteModalLabel button[name=_rr_delete_ok]", {'optype': 1}, RecordDel);

    // DNS记录展示页的操作绑定事件--状态操作按钮(记录状态操作确认)
    // $("table a[action_type=status]").bind('click', RecordStatusACK);
    $(document).on("click", "#table_record_list a[action_type=status]", {'optype': 1},  RecordStatusACK);
    $(document).on("click", ".rr-status-operate button[action_type=status]", {'optype': 2},  RecordStatusACK);

    // 记录状态操作 确认按钮绑定事件（执行记录状态操作）
    // $("#RecordStatusModalLabel button[name=_modify_status_ok]").bind('click', RedcordStatusModify);
    $(document).on("click", "#RecordStatusModalLabel button[name=_modify_status_ok]", RedcordStatusModify);

    // DNS记录展示页的操作绑定事件--修改操作按钮
    // $("table a[action_type=modify]").bind('click', RecordModifyACK);
    $(document).on("click", "table a[action_type=modify]", RecordModifyACK);

    // 分页导航绑定点击事件
    // $(".pagination a").bind('click', ClickPage);
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
    $(document).on("click", "div button[name=dns_record_search_submit]", RecordSearch);

    // 域名解析页 搜索按钮绑定事件
    $(document).on("click", "div button[name=domain_resolution_search_submit]", DomainResolutionSearch);

    // 我的域名页 搜索按钮绑定事件
    $(document).on("click", "div button[name=domain_search_submit]", DomainSearch);

    // 点击 添加域名 弹出添加域名页（添加域名确认操作页面）
    $(document).on("click", "button[name=add_domain]", DoaminAddACK);
    // 修改domain确认框
    $(document).on("click", "#domain_box li a[action_type=modify]", DoaminModifyACK);
    // 点击 添加域名/修改域名 确认操作
    $(document).on("click", "#DomainAddOrModifyModalLabel button[name=_save]", DoaminAddModify);

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
    $(document).on("click", "button[name=import_dns_confirm]", ImportRecordACK);

    // 点击 导出DNS解析记录 按钮
    $(document).on("click", "#table_domains ul li a[action_type=_export_records]", ExportRecord);

    // 确认 导出DNS解析记录
    $(document).on("click", "button[name=_export_dns_record_ok]", ExportRecordACK);

    // 鼠标移动到 record 记录值时显示复制按钮,离开时隐藏
    $(document).on("mouseenter", "#table_record_list .record_data", {'val': true}, ShowRecordDataCopyButton)
    $(document).on("mouseleave", "#table_record_list .record_data", {'val': false}, ShowRecordDataCopyButton)

    // 导入DNS解析记录时，mx_priority input框是否可输入
    $(document).on("change", '#table_import_dns select[name=type]', MxPriorityInputAutoDisable);

    // input 框内的 x，清空该 input 输入的内容
    $(document).on("click", "span[name=clear-previous-input]", ClearPreviousInput);
});


