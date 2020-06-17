import smtplib
import hashlib
import re
import time
import random
import difflib
from email.mime.text import MIMEText
from email.header import Header
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from housemaster.models import *
from django.shortcuts import render
from django.core.paginator import Paginator



# ----------------------------------------工具：发送邮件的类
class Mail(object):
    def __init__(self, receivers, content, sender='1039459472@qq.com'):
        # 第三方 SMTP 服务
        self.mail_host = "smtp.qq.com"  # 设置服务器:这个是qq邮箱服务器，直接复制就可以
        self.mail_pass = "iwhgqggzqkeebbgi"  # 刚才我们获取的授权码
        self.sender = sender  # 发送方邮件人
        self.receivers = receivers  # 收件人的邮箱（可多个）
        self.content = content
        self.send()

    def send(self):
        message = MIMEText(self.content, 'plain', 'utf-8')
        message['From'] = Header("", 'utf-8')
        message['To'] = Header("", 'utf-8')
        subject = '来自宿舍管理系统的重要邮件！'  # 发送的主题，可自由填写
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = smtplib.SMTP_SSL(self.mail_host, 465)
            smtpObj.login(self.sender, self.mail_pass)
            smtpObj.sendmail(self.sender, self.receivers, message.as_string())
            smtpObj.quit()
        except smtplib.SMTPException:
            print('邮件发送失败')


# ----------------------------------------工具：登录装饰器
def LoginDescribe(func):
    # 1.获取cookie中的email和session的信息
    # 2.判断email是不是相等，成功跳转，失败返回登录页
    def inner(request, *args, **kwargs):
        cookie_stu_id = request.COOKIES.get('stu_id')
        session_stu_id = request.session.get('stu_id')
        if cookie_stu_id == session_stu_id and cookie_stu_id and session_stu_id:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/user/login/')

    return inner


# ----------------------------------------工具：使用md5算法加密密码
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


# ---------------------------------------工具：登录页随机生成一句话
def random_sentence():
    sentence = [
        '思念的心会不自觉的痛，你可知道。',
        '我喜欢蒲公英，她甘于寂寞，甘于平凡。',
        '因为太怕失去你，所以连快乐里也装满悲伤。',
        '莫以善小而不为，莫以恶小而为之。',
        '心量狭小，则多烦恼，心量广大，智慧丰饶。',
    ]
    return random.choice(sentence)


# ====================================注册功能（ajax）=============================================
def register(request):
    dor = Dor.objects.all()
    return render(request, 'user/register.html', locals())


def register_ajax_data(request):
    stastus = request.GET.get('status')  # 获取按钮要操作的状态
    result = {}
    if request.method == 'POST':
        stu_id = request.POST.get('stu_id')
        password = request.POST.get('password')
        email = request.POST.get('email')
        name = request.POST.get('user_name')
        sex = request.POST.get('sex')
        dor = request.POST.get('dor')
        # 发送邮箱
        if stastus == '1':
            if stu_id and not Stu.objects.filter(stu_id=stu_id).first():
                pattern_email = re.findall('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email)  # #邮箱正则
                if pattern_email:
                    try:
                        random_emailcode = str(random.randint(1000, 9999))  # 随机生成四位数验证码
                        Verification.objects.create(email=email, verification_code=random_emailcode,
                                                    create_time=time.time())
                        email_content = "你的邮箱验证码为%s " % random_emailcode
                        Mail(receivers=email, content=email_content)  # 发送邮件的类
                        result = {'code': 10000, 'content': '提示：发送邮箱验证码成功，请去邮箱接收，有效期1分钟'}
                    except:
                        result = {'code': 10001, 'content': '提示：发送失败，遇到错误，可能邮箱不正确或者网络有误！'}
                else:
                    result = {'code': 10002, 'content': '提示：请输入正确的邮箱'}
            else:
                result = {'code': 10003, 'content': '提示：你还没有输入账号或者账户以及存在！'}
        # 用户注册
        if stastus == '2':
            # 首先输入的信息不为空
            emailcode = request.POST.get('emailcode')
            if stu_id and password and email and emailcode and name and sex and dor:
                # 然后数据库中没有此账户存在
                user = Stu.objects.filter(stu_id=stu_id).first()
                if not user:
                    # 不存在判断邮箱验证码是否相同，或者过了时间
                    ver = Verification.objects.filter(email=email).last()  # 查找该邮箱的最后一个验证码
                    if ver and ver.verification_code == emailcode and time.time() - ver.create_time <= 60:
                        # 如果自己性别与该宿舍宿舍性别不符合，则无法注册
                        dor_ = Dor.objects.filter(num=dor).first()
                        if dor_.sex == sex:
                            # 成功后，宿舍现存人数加一
                            Stu.objects.create(password=setPassword(password), stu_id=stu_id, email=email, name=name,
                                               dor=Dor.objects.filter(num=dor).first(), sex=sex)
                            dor_.now_people += 1
                            dor_.save()
                            result = {'code': 10000, 'content': '恭喜!账户【%s】注册成功!' % stu_id}
                        else:
                            result = {'code': 10008, 'content': '提示信息：失败！性别不符该宿舍'}
                    else:
                        result = {'code': 10007, 'content': '提示信息:验证码失效或者输入错误！'}
                else:
                    result = {'code': 10005, 'content': '提示信息:账户【%s】已存在！请再想个新的账号' % stu_id}
            else:
                result = {'code': 10004, 'content': '提示信息:请检查，信息还没填全！'}
    return JsonResponse(result)


# ====================================登录功能=====================================================
def login(request):
    result = {'code': 00000, 'content': random_sentence()}
    if request.method == "POST":
        stu_id = request.POST.get('stu_id')
        password = request.POST.get('password')
        # 如果账户密码都不为空
        if stu_id and password:
            # 判断账户是否存在
            has_stu_id = Stu.objects.filter(stu_id=stu_id).first()
            if has_stu_id:
                if setPassword(password) == has_stu_id.password:
                    # 密码成功就设置cookie和session
                    response = HttpResponseRedirect('/user/index2/')
                    response.set_cookie('stu_id', stu_id)
                    request.session['stu_id'] = stu_id
                    result['code'] = 10000
                    return response
                else:
                    result = {'code': 3, 'content': '提示信息：密码输入错误！'}
            else:
                result = {'code': 2, 'content': '提示信息:账户【%s】不存在！' % stu_id}
        else:
            result = {'code': 1, 'content': '提示信息:信息还没填全呦！'}

    return render(request, 'user/login.html', locals())


# ====================================退出登录功能=================================================
def logout(request):
    # 删除cookie和session
    response = HttpResponseRedirect('/user/login/')  # 返回登录页
    del request.session['stu_id']
    response.delete_cookie('stu_id')  # 删除指定cookie
    response.delete_cookie('sessionid')  # 删除指定cookie
    return response


# ====================================忘记密码（ajax）=============================================
def forgot_password(request):
    return render(request, 'user/forgot_password.html')


def forgot_password_ajax(request):
    stastus = request.GET.get('status')  # 获取按钮要操作的状态
    result = {'code': 00000, 'content': '提示信息：无'}
    if request.method == "POST":
        stu_id = request.POST.get('stu_id')
        email = request.POST.get('email')
        # 发送邮箱验证码
        if stastus == '1':
            if stu_id and email:
                has_stu_id = Stu.objects.filter(stu_id=stu_id).first()
                if has_stu_id:
                    # 判断邮箱是否正确
                    if has_stu_id.email == email:
                        try:
                            random_emailcode = str(random.randint(1000, 9999))  # 随机生成四位数验证码
                            Verification.objects.create(email=email, verification_code=random_emailcode,
                                                        create_time=time.time())
                            email_content = "你的邮箱验证码为%s " % random_emailcode
                            Mail(receivers=email, content=email_content)  # 发送邮件的类
                            result = {'code': 10000, 'content': '提示：发送邮箱验证码成功，请去邮箱接收，有效期1分钟'}
                        except:
                            result = {'code': 10001, 'content': '提示：发送失败，遇到错误，可能邮箱不正确或者网络有误！'}
                    else:
                        result = {'code': 10008, 'content': '提示信息:邮箱不正确！'}
                else:
                    result = {'code': 10009, 'content': '提示信息:账户不存在！'}
            else:
                result = {'code': 10009, 'content': '提示信息:请填写完整以后再发送...'}
        # 找回密码
        if stastus == '2':
            emailcode = request.POST.get('emailcode')
            # 判断是否填写
            if stu_id and email and emailcode:
                # 判断账户是否存在
                has_stu_id = Stu.objects.filter(stu_id=stu_id).first()
                if has_stu_id:
                    # 判断邮箱是否正确
                    if has_stu_id.email == email:
                        # 如果有幸正确，判断输入验证码是否过期或者错误
                        ver = Verification.objects.filter(email=email).last()  # 查找该邮箱的最后一个验证码
                        if ver and ver.verification_code == emailcode and time.time() - ver.create_time <= 60:
                            password = str(random.randint(10000000, 99999999))
                            has_stu_id.password = setPassword(password)
                            has_stu_id.save()
                            email_content = "亲爱的同学你好：由于你忘记密码，因此我们将重新设置你的密码，你的新密码为【%s】,请尽快登陆进入个人中心页进行修改密码！！ " % password
                            Mail(receivers=email, content=email_content)
                            result = {'code': 10000, 'content': '提示：密码已经修改，请去邮箱查看新密码，请尽快登录更改密码！'}
                        else:
                            result = {'code': 10007, 'content': '提示信息:验证码失效或者输入错误！'}
                    else:
                        result = {'code': 10008, 'content': '提示信息:邮箱不正确！'}
                else:
                    result = {'code': 10009, 'content': '提示信息:账户不存在！'}
            else:
                result = {'code': 10010, 'content': '提示信息:请填写完整以后再发送...'}
    return JsonResponse(result)


# -------------------------------------------------------------------未登录主页路由
def index1(request):
    return render(request, 'user/index1.html', locals())


# --------------------------------------------------------------------登录后主页路由
@LoginDescribe
def index2(request):
    stu_id = request.COOKIES.get('stu_id')
    user = Stu.objects.filter(stu_id=stu_id).first()
    return render(request, 'user/index2.html', locals())


# -------------------------------------------------------------------关于我们页面
@LoginDescribe
def about(request):
    return render(request, 'user/about.html', locals())


# --------------------------------------------------------------------修改个人信息（ajax）
@LoginDescribe
def update_info(request):
    stu_id = request.COOKIES.get('stu_id')
    user = Stu.objects.filter(stu_id=stu_id).first()
    return render(request, 'user/update_info.html', locals())


def update_info_ajax(request):
    stu_id = request.COOKIES.get('stu_id')
    user = Stu.objects.filter(stu_id=stu_id).first()
    content = {'content': ''}
    if request.method == 'POST':
        phone1 = request.POST.get('phone1')
        name1 = request.POST.get('name1')
        major_class = request.POST.get('major_class')
        birthday = request.POST.get('birthday')
        remarks = request.POST.get('remarks')
        print(name1, phone1, major_class, birthday, remarks)
        if phone1 and name1 and major_class and birthday:
            pattern_phone = re.findall('^1[3456789]\d{9}$', phone1)  # #电话正则
            pattern_bir = re.findall('^(19|20)\d{2}-(1[0-2]|0?[1-9])-(0?[1-9]|[1-2][0-9]|3[0-1])$', birthday)  # 生日的正则
            if pattern_bir and pattern_bir:
                user.phone = phone1
                user.name = name1
                user.major_class = major_class
                user.birthday = birthday
                user.remarks = remarks
                user.save()
                content = {'content': '修改成功！'}
            else:
                content = {'content': '电话或者生日格式非法！'}
        else:
            content = {'content': '信息未填写完整！备注可不填'}

    return JsonResponse(content)


# --------------------------------------------------------------------修改密码
@LoginDescribe
def update_password(request):
    stu_id = request.COOKIES.get('stu_id')
    user = Stu.objects.filter(stu_id=stu_id).first()
    content = '提示信息：你正在修改个人密码...修改成功后返回登录页'
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        print(old_password, new_password1, new_password2)
        # 必须全部填写
        if old_password and new_password1 and new_password2:
            user = Stu.objects.filter(stu_id=stu_id).first()
            password = user.password
            # 判断旧密码是否正确
            if setPassword(old_password) == password:
                # 判断两个新密码是否相同
                if new_password1 == new_password2:
                    # 判断新密码是否与旧密码相同
                    if setPassword(new_password1) != password:
                        user.password = setPassword(new_password1)
                        user.save()
                        # 删除cookie和session
                        response = HttpResponseRedirect('/user/login/')  # 返回登录页
                        del request.session['stu_id']
                        response.delete_cookie('stu_id')  # 删除指定cookie
                        response.delete_cookie('sessionid')  # 删除指定cookie
                        return response

                    else:
                        content = '提示信息:新密码不可与旧密码相同...'
                else:
                    content = '提示信息:两次新密码输入不一致'
            else:
                content = '提示信息:旧密码输入错误...'
        else:
            content = '提示信息:请填写完整以后再发送...'
    return render(request, 'user/update_password.html', locals())


# ------------------------------------------------------------更换宿舍
@LoginDescribe
def update_dor_form(request):
    content = '正在填写申请单...'
    stu_id = request.COOKIES.get('stu_id')
    user = Stu.objects.filter(stu_id=stu_id).first()
    all_dor = Dor.objects.all()
    if request.method == 'POST':
        name = user.name
        sex = user.sex
        dor = request.POST.get('dor')
        remarks = request.POST.get('remarks')
        major_class = request.POST.get('major_class')
        remarks = request.POST.get('remarks')

        # 判断表单是否填写完整
        if name and sex and dor:
            # 判断宿舍性别和个人性别是否符合
            dor_ = Dor.objects.filter(num=dor).first()
            # 判断更换前的宿舍和更换后宿舍是否相同
            if user.dor.num != dor:
                if dor_.sex == sex:
                    # 判断最近一次的提交单是否处理，未处理不可以新建
                    change_dor = Change_dor.objects.filter(stu_id=stu_id).last()
                    if not change_dor:
                        if not remarks:
                            remarks = '无'
                        change_dor = Change_dor.objects.create(
                            stu_id=stu_id,
                            name=name,
                            sex=sex,
                            major_class=major_class,
                            now_dor=user.dor.num,
                            go_dor=dor,
                            remarks=remarks,
                            send_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        )
                        content = '成功！已提交至管理员处'
                        time.sleep(2)
                        return HttpResponseRedirect('/user/update_dor_history/')
                    else:
                        if change_dor.status != 0:
                            if not remarks:
                                remarks = '无'
                            change_dor = Change_dor.objects.create(
                                stu_id=stu_id,
                                name=name,
                                sex=sex,
                                major_class=major_class,
                                now_dor=user.dor.num,
                                go_dor=dor,
                                remarks=remarks,
                                send_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                            )
                            content = '成功！已提交至管理员处'
                        else:
                            content = '失败！上次申请还未处理！'

                else:
                    content = '想得美！性别和宿舍不符！'
            else:
                content = '失败！你已经在{}宿舍了'.format(dor)
        else:
            content = '失败！请填写完整后再提交'
        print(content)
    return render(request, 'user/update_dor_form.html', locals())


# ——----------------------------------------------------更换宿舍历史
@LoginDescribe
def update_dor_history(request, del_id='无'):
    # 查询到本学生的所有申请宿舍更换历史
    stu_id = request.COOKIES.get('stu_id')
    user = Stu.objects.filter(stu_id=stu_id).first()
    update_dor_form = Change_dor.objects.filter(stu_id=stu_id).order_by('-id')
    # 获取撤销按钮的订单号
    if del_id != '无':
        del_id = int(del_id)
        Change_dor.objects.get(id=del_id).delete()
    return render(request, 'user/update_dor_history.html', locals())


# ----------------------------------------------------宿舍维修表单
@LoginDescribe
def fix_dor_form(request):
    content = '正在填写维修单...'
    stu_id = request.COOKIES.get('stu_id')
    user = Stu.objects.filter(stu_id=stu_id).first()
    all_dor = Dor.objects.all()
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        detail_remarks = request.POST.get('remarks')
        dor = request.POST.get('dor')
        simple_remarks = detail_remarks[:10] + '...'
        if name and detail_remarks and dor and phone:
            pattern_phone = re.findall('^1[3456789]\d{9}$', phone)  # #电话正则
            if pattern_phone:
                fix_dor = Fix_dor.objects.create(
                    stu_id=stu_id,
                    name=name,
                    phone=phone,
                    dor=dor,
                    detail_remarks=detail_remarks,
                    simple_remarks=simple_remarks,
                    send_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                )
                time.sleep(2)
                return HttpResponseRedirect('/user/fix_dor_history/')
            else:
                content = '失败！电话格式不正确'
        else:
            content = '失败！填写不完整！'
    return render(request, 'user/fix_dor_form.html', locals())


# ----------------------------------------------------宿舍维修表单修改
@LoginDescribe
def fix_dor_form_update(request, id):
    content = '正在修改维修单...'
    all_dor = Dor.objects.all()  # 查询所有宿舍
    fix = Fix_dor.objects.get(id=int(id))  # 查询该订单的信息
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        detail_remarks = request.POST.get('remarks')
        dor = request.POST.get('dor')
        simple_remarks = detail_remarks[:8] + '...'
        if name and detail_remarks and dor:
            pattern_phone = re.findall('^1[3456789]\d{9}$', phone)  # #电话正则
            if pattern_phone:
                fix_dor = Fix_dor.objects.get(id=id)
                fix_dor.name = name
                fix_dor.phone = phone
                fix_dor.dor = dor
                fix_dor.detail_remarks = detail_remarks
                fix_dor.simple_remarks = simple_remarks
                fix_dor.send_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                fix_dor.save()
                content = '修改成功！'
            else:
                content = '失败！电话格式不正确'
        else:
            content = '失败！填写不完整！'
    return render(request, 'user/fix_dor_form_update.html', locals())


# --------------------------------------------------------宿舍维修历史
@LoginDescribe
def fix_dor_history(request, del_id='无'):
    # 查询到本学生的所有申请宿舍更换历史
    stu_id = request.COOKIES.get('stu_id')
    user = Stu.objects.filter(stu_id=stu_id).first()
    fix_dor_form = Fix_dor.objects.filter(stu_id=stu_id).order_by('-id')
    if del_id != '无':
        del_id = int(del_id)
        Fix_dor.objects.get(id=del_id).delete()
    return render(request, 'user/fix_dor_history.html', locals())


# -------------------------------------------投诉管理员页面（会发送至管理员邮箱），使用ajax
def complaint(request):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    user = User.objects.all()

    return render(request, 'user/complaint.html', locals())


def complaint_ajax(request):
    content = {'code': 10000, 'content': '提示信息：无'}
    if request.method == 'POST':
        admin = request.POST.get('admin')  # 宿管名字
        detail = request.POST.get('detail')  # 详细原因
        stu_name = request.POST.get('stu_name')
        phone = request.POST.get('phone')
        # 编辑邮件
        msg = '''亲爱的管理员：
            您好！我想向您举报的是【{}】。
            详细情况是：【{}】！
            我的姓名是：【{}】，我的联系电话是：【{}】。
            希望这个邮件，能引起您的重视！祝生活愉快！
            '''.format(admin, detail, stu_name, phone)
        if admin and detail and detail:
            try:
                Mail(receivers='1039459472@qq.com', content=msg, sender='1039459472@qq.com')
                content = {'code': 10000, 'content': '举报成功！举报信息已发送至管理员邮箱！'}
            except:
                content = {'code': 10001, 'content': '举报失败！接收人邮箱有误！你可以拨打举报电话：15888888888'}
        else:
            content = {'code': 10002, 'content': '举报失败！信息没有填完整！'}
    return JsonResponse(content)


# -----------------------------------------意见或者建议
def opinions(request):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    user = User.objects.all()

    return render(request, 'user/opinions.html', locals())


def opinions_ajax(request):
    content = {'code': 10000, 'content': '提示信息：无'}
    if request.method == 'POST':
        detail = request.POST.get('detail')  # 详细原因
        stu_name = request.POST.get('stu_name')
        phone = request.POST.get('phone')
        pattern_phone = re.findall('^1[3456789]\d{9}$', phone)  # #电话正则
        # 编辑邮件
        msg = '''亲爱的管理员：       
            我的姓名是：【{}】，我的联系电话是：【{}】。
            我有一些意见和建议：【{}】！
            希望这个邮件，能引起您的重视！祝生活愉快！
            '''.format(stu_name, phone, detail)
        if stu_name and phone and detail:
            if pattern_phone:
                try:
                    Mail(receivers='1039459472@qq.com', content=msg, sender='1039459472@qq.com')
                    content = {'code': 10000, 'content': '发送成功！建议已发送至管理员邮箱！'}
                except:
                    content = {'code': 10001, 'content': '发送失败！接收人邮箱有误！你可以拨打电话：15888888888'}
            else:
                content = {'code': 10004, 'content': '发送失败！手机号非法！需要去个人信息处修改！'}
        else:
            content = {'code': 10002, 'content': '发送失败！信息没有填完整！'}
    return JsonResponse(content)


# -------------------------------------------------公告列表
def notice_list(request):
    notice = Notice.objects.all().order_by('-id')
    return render(request, 'user/notice_list.html', locals())


# ------------------------------------------------宿舍管理员列表信息
def housemaster(request):
    housemaster = User.objects.all()
    return render(request, 'user/housemaster.html', locals())


# -------------------------------------------------公告查看
def notice_look(request, id):
    notice = Notice.objects.get(id=int(id))
    return render(request, 'user/notice_look.html', locals())


# -----------------------------------------------物品报失首页
def goods_index(request):
    return render(request, 'user/goods_index.html', locals())


# -----------------------------------------------物品丢失发布
class GoodsInfo:
    def __init__(self):
        self.location_list = ['通方教学楼', '思源教学楼', '知行教学楼', '行政办公楼', '实验楼①', '实验楼②', '男生宿舍楼', '女生宿舍楼', '菜鸟驿站', '西北角操场',
                              '图书馆',
                              '医务楼', '学校东门', '学校南门', '学校西门', '学校北门', '一期超市', '一期食堂', '二期超市']
        self.type_list = ['衣物', '书籍', '数码设备', '日用品', '食物', '材料', '钥匙', '其他', ]
        self.Y_list = ['2020']
        self.M_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        self.D_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
                       '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
        self.h_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
                       '17', '18', '19', '20', '21', '22', '23', '24']
        self.m_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
                       '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32',
                       '33',
                       '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
                       '50',
                       '51', '52', '53', '54', '55', '56', '57', '58', '59']
        self.s_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
                       '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32',
                       '33',
                       '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
                       '50',
                       '51', '52', '53', '54', '55', '56', '57', '58', '59']


# -----------------------------------------------物品丢失信息发布
def goods_loss_send(request):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    goods_info = GoodsInfo()
    if request.method == 'POST':
        loss_name = request.POST.get('loss_name')
        loss_phone = request.POST.get('loss_phone')
        loss_goods_name = request.POST.get('loss_goods_name')
        loss_Y = request.POST.get('loss_Y')
        loss_M = request.POST.get('loss_M')
        loss_D = request.POST.get('loss_D')
        loss_h = request.POST.get('loss_h')
        loss_m = request.POST.get('loss_m')
        loss_s = request.POST.get('loss_s')
        loss_time = '{}-{}-{} {}:{}:{}'.format(loss_Y, loss_M, loss_D, loss_h, loss_m, loss_s)
        loss_location = request.POST.get('loss_location')
        loss_type = request.POST.get('loss_type')
        loss_remarks = request.POST.get('loss_remarks')
        loss_picture = request.FILES.get('picture')
        if loss_name and loss_phone and loss_goods_name and loss_time and loss_location and loss_type:
            pattern_phone = re.findall('^1[3456789]\d{9}$', loss_phone)  # #电话正则
            if pattern_phone:
                loss_goods = Loss_goods()
                loss_goods.stu_id = stu_id
                loss_goods.loss_name = loss_name
                loss_goods.loss_phone = loss_phone
                loss_goods.loss_goods_name = loss_goods_name
                loss_goods.loss_time = loss_time
                loss_goods.loss_location = loss_location
                loss_goods.loss_type = loss_type
                loss_goods.send_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                if loss_remarks is not None:
                    loss_goods.loss_remarks = loss_remarks
                if loss_picture is not None:
                    loss_goods.loss_picture = loss_picture
                loss_goods.save()
                result = '发布失物成功！'
            else:
                result = '电话格式非法！请务必填写正确的联系电话！'
        else:
            result = '必要信息必须填写完毕！'
    return render(request, 'user/goods_loss_send.html', locals())


# -----------------------------------------------物品丢失信息查看
def goods_loss_look(request):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    # 物品信息回填
    id = request.GET.get('id')
    loss_goods = Loss_goods.objects.filter(id=int(id)).first()
    # 找到物品改变状态
    status = request.GET.get('status')
    if status:
        if int(status) == 1:
            loss_goods.status = 1
            loss_goods.save()
    return render(request, 'user/goods_loss_look.html', locals())


# -----------------------------------------------物品拾取发布
def goods_pickup_send(request):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    goods_info = GoodsInfo()
    if request.method == 'POST':
        pickup_name = request.POST.get('pickup_name')
        pickup_phone = request.POST.get('pickup_phone')
        pickup_goods_name = request.POST.get('pickup_goods_name')
        pickup_Y = request.POST.get('pickup_Y')
        pickup_M = request.POST.get('pickup_M')
        pickup_D = request.POST.get('pickup_D')
        pickup_h = request.POST.get('pickup_h')
        pickup_m = request.POST.get('pickup_m')
        pickup_s = request.POST.get('pickup_s')
        pickup_time = '{}-{}-{} {}:{}:{}'.format(pickup_Y, pickup_M, pickup_D, pickup_h, pickup_m, pickup_s)
        pickup_location = request.POST.get('pickup_location')
        pickup_type = request.POST.get('pickup_type')
        pickup_remarks = request.POST.get('pickup_remarks')
        pickup_picture = request.FILES.get('picture')
        if pickup_name and pickup_phone and pickup_goods_name and pickup_time and pickup_location and pickup_type:
            pattern_phone = re.findall('^1[3456789]\d{9}$', pickup_phone)  # #电话正则
            if pattern_phone:
                pickup_goods = Pickup_goods()
                pickup_goods.pickup_name = pickup_name
                pickup_goods.stu_id = stu_id
                pickup_goods.pickup_phone = pickup_phone
                pickup_goods.pickup_goods_name = pickup_goods_name
                pickup_goods.pickup_time = pickup_time
                pickup_goods.pickup_location = pickup_location
                pickup_goods.pickup_type = pickup_type
                pickup_goods.send_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                if pickup_remarks is not None:
                    pickup_goods.pickup_remarks = pickup_remarks
                if pickup_picture is not None:
                    pickup_goods.pickup_picture = pickup_picture
                pickup_goods.save()
                result = '发布拾取信息成功！'
            else:
                result = '电话格式非法！请务必填写正确的联系电话！'
        else:
            result = '必要信息必须填写完毕！'
    return render(request, 'user/goods_pickup_send.html', locals())


# -----------------------------------------丢失信息列表
def loss_list(request, page=1):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    loss_goods = Loss_goods.objects.all().order_by('-id')
    paginator = Paginator(loss_goods, 6)  # 分页一页显示6条
    page_obj = paginator.page(int(page))

    # 删除
    del_id = request.GET.get('del_id')
    if del_id:
        del_id = int(del_id)
        Loss_goods.objects.get(id=del_id).delete()
    # 搜索框
    search = request.GET.get('search')
    if search:
        loss_goods = Loss_goods.objects.filter(loss_goods_name__contains=search)
        if not loss_goods:
            result = '无结果！查询所有！'
        else:
            paginator = Paginator(loss_goods, 7)  # 分页一页显示6条
            page_obj = paginator.page(int(page))
    return render(request, 'user/loss_list.html', locals())


# -----------------------------------------拾取信息列表
def pickup_list(request, page=1):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    pickup_goods = Pickup_goods.objects.all().order_by('-id')
    paginator = Paginator(pickup_goods, 6)  # 分页一页显示7条
    page_obj = paginator.page(int(page))

    # 删除
    del_id = request.GET.get('del_id')
    if del_id:
        del_id = int(del_id)
        Pickup_goods.objects.get(id=del_id).delete()
    # 搜索框
    search = request.GET.get('search')
    if search:
        pickup_goods = Pickup_goods.objects.filter(pickup_goods_name__contains=search)
        if not pickup_goods:
            result = '无结果！查询所有！'
        else:
            paginator = Paginator(pickup_goods, 8)  # 分页一页显示六条
            page_obj = paginator.page(int(page))
    return render(request, 'user/pickup_list.html', locals())


# -----------------------------------------------拾取物品信息查看
def goods_pickup_look(request):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    # 物品信息回填
    id = request.GET.get('id')
    pickup_goods = Pickup_goods.objects.filter(id=int(id)).first()
    # 找到物品改变状态
    status = request.GET.get('status')
    if status:
        if int(status) == 1:
            pickup_goods.status = 1
            pickup_goods.save()
    return render(request, 'user/goods_pickup_look.html', locals())


# -----------------------------------------------智能推荐疑似物品
def loss_ai(request):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    # 找到自己的物品
    id = request.GET.get('id')
    loss_goods = Loss_goods.objects.filter(id=int(id)).first()
    # 智能推荐算法
    GoodsInfo = []
    # 查询所有未处理的拾取物品订单
    pickup_goods_all = Pickup_goods.objects.filter(status=0)
    if pickup_goods_all:
        # 将拾取的所有物品的每一个物品信息放在一个单独的字典,并存入列表
        for i in pickup_goods_all:
            info = {'id': i.id, 'pickup_goods_name': i.pickup_goods_name, 'pickup_remarks': i.pickup_remarks,
                    'pickup_location': i.pickup_location, 'pickup_time': i.pickup_time, 'pickup_type': i.pickup_type,
                    'score': 0}
            GoodsInfo.append(info)
        for goods in GoodsInfo:
            # ①判断这些物品中的丢失地方、物品类型是否相同(两项占总成绩的20分)
            if goods['pickup_type'] == loss_goods.loss_type:
                goods['score'] += 10
            if goods['pickup_location'] == loss_goods.loss_location:
                goods['score'] += 10
            # ②判断名字和备注的相似度（越高分值越大，占总成绩的50分,名字占20，备注占30）
            remarks_difflib = difflib.SequenceMatcher(None, loss_goods.loss_remarks, goods['pickup_remarks']).ratio()
            goods_name_difflib = difflib.SequenceMatcher(None, loss_goods.loss_goods_name,
                                                         goods['pickup_goods_name']).ratio()
            goods['score'] += remarks_difflib * 100 * 0.3 + goods_name_difflib * 100 * 0.2

            # ③判断丢失时间是否相近（占总成绩30分）
            # 由于丢失时间设定之前未判断闰年和未判断每月日期有几天，所以需要此处判断
            time_ = loss_goods.loss_time[:10].split('-')
            # 时间需要属于正确月份的天数
            if int(time_[1]) in [1, 3, 5, 7, 8, 10, 12] and int(time_[2]) <= 31 or int(time_[1]) in [4, 6, 9,
                                                                                                     11] and int(
                time_[2]) <= 30 or int(time_[0]) % 4 == 0 and int(time_[0]) % 100 != 0 and int(
                time_[1]) == 2 and int(
                time_[2]) <= 29 or int(time_[0]) % 400 == 0 and int(time_[1]) == 2 and int(time_[2]) <= 29:
                # 将时间转换为时间戳
                time_cuo = time.mktime(time.strptime(loss_goods.loss_time, '%Y-%m-%d %H:%M:%S'))
                # 捡到的时间处理
                time_ = goods['pickup_time'][:10].split('-')
                if int(time_[1]) in [1, 3, 5, 7, 8, 10, 12] and int(time_[2]) <= 31 or int(time_[1]) in [4, 6, 9,
                                                                                                         11] and int(
                    time_[2]) <= 30 or int(time_[0]) % 4 == 0 and int(time_[0]) % 100 != 0 and int(
                    time_[1]) == 2 and int(
                    time_[2]) <= 29 or int(time_[0]) % 400 == 0 and int(time_[1]) == 2 and int(time_[2]) <= 29:
                    # 将时间转换为时间戳
                    pick_time_cuo = time.mktime(time.strptime(goods['pickup_time'], '%Y-%m-%d %H:%M:%S'))
                    # 都符合时间规则
                    if time_cuo >= pick_time_cuo:
                        # 时间戳一天相差60*60*24=86400
                        if time_cuo - pick_time_cuo <= 86400:
                            goods['score'] += 30
                        elif 86400 < time_cuo - pick_time_cuo <= 86400 * 5:
                            goods['score'] += 15
                        else:
                            goods['score'] += 5
                    elif pick_time_cuo >= time_cuo:
                        # 时间戳一天相差60*60*24=86400
                        if pick_time_cuo - time_cuo <= 86400:
                            goods['score'] += 30
                        elif 86400 < pick_time_cuo - time_cuo <= 86400 * 5:
                            goods['score'] += 15
                        else:
                            goods['score'] += 5
            # 选出最符合的物品，挑选分数最大的
            max_score_goods = max(GoodsInfo, key=lambda n: n['score'])
            max_score = str(max_score_goods['score'])[:4]
            # 根据选出分数的最大的，查找数据库中该物品的信息
            foo = Pickup_goods.objects.filter(id=max_score_goods['id']).first()
    return render(request, 'user/loss_ai.html', locals())


# -----------------------------------------------智能推荐疑似失主
def pickup_ai(request):
    stu_id = request.COOKIES.get('stu_id')
    stu = Stu.objects.filter(stu_id=stu_id).first()
    # 找到自己的物品
    id = request.GET.get('id')
    pickup_goods = Pickup_goods.objects.filter(id=int(id)).first()
    # 智能推荐算法
    GoodsInfo = []
    # 查询所有未处理的拾取物品订单
    loss_goods_all = Loss_goods.objects.filter(status=0)
    if loss_goods_all:
        # 将拾取的所有物品的每一个物品信息放在一个单独的字典,并存入列表
        for i in loss_goods_all:
            info = {'id': i.id, 'loss_goods_name': i.loss_goods_name, 'loss_remarks': i.loss_remarks,
                    'loss_location': i.loss_location, 'loss_time': i.loss_time, 'loss_type': i.loss_type,
                    'score': 0}
            GoodsInfo.append(info)
        for goods in GoodsInfo:
            # ①判断这些物品中的丢失地方、物品类型是否相同(两项占总成绩的20分)
            if goods['loss_type'] == pickup_goods.pickup_type:
                goods['score'] += 10
            if goods['loss_location'] == pickup_goods.pickup_location:
                goods['score'] += 10
            # ②判断名字和备注的相似度（越高分值越大，占总成绩的50分,名字占20，备注占30）
            remarks_difflib = difflib.SequenceMatcher(None, pickup_goods.pickup_remarks, goods['loss_remarks']).ratio()
            goods_name_difflib = difflib.SequenceMatcher(None, pickup_goods.pickup_goods_name,
                                                         goods['loss_goods_name']).ratio()
            goods['score'] += remarks_difflib * 100 * 0.3 + goods_name_difflib * 100 * 0.2

            # ③判断丢失时间是否相近（占总成绩30分）
            # 由于丢失时间设定之前未判断闰年和未判断每月日期有几天，所以需要此处判断
            time_ = pickup_goods.pickup_time[:10].split('-')
            # 时间需要属于正确月份的天数
            if int(time_[1]) in [1, 3, 5, 7, 8, 10, 12] and int(time_[2]) <= 31 or int(time_[1]) in [4, 6, 9,
                                                                                                     11] and int(
                time_[2]) <= 30 or int(time_[0]) % 4 == 0 and int(time_[0]) % 100 != 0 and int(
                time_[1]) == 2 and int(
                time_[2]) <= 29 or int(time_[0]) % 400 == 0 and int(time_[1]) == 2 and int(time_[2]) <= 29:
                # 将时间转换为时间戳
                time_cuo = time.mktime(time.strptime(pickup_goods.pickup_time, '%Y-%m-%d %H:%M:%S'))
                # 捡到的时间处理
                time_ = goods['loss_time'][:10].split('-')
                if int(time_[1]) in [1, 3, 5, 7, 8, 10, 12] and int(time_[2]) <= 31 or int(time_[1]) in [4, 6, 9,
                                                                                                         11] and int(
                    time_[2]) <= 30 or int(time_[0]) % 4 == 0 and int(time_[0]) % 100 != 0 and int(
                    time_[1]) == 2 and int(
                    time_[2]) <= 29 or int(time_[0]) % 400 == 0 and int(time_[1]) == 2 and int(time_[2]) <= 29:
                    # 将时间转换为时间戳
                    pick_time_cuo = time.mktime(time.strptime(goods['loss_time'], '%Y-%m-%d %H:%M:%S'))
                    # 都符合时间规则
                    if time_cuo >= pick_time_cuo:
                        # 时间戳一天相差60*60*24=86400
                        if time_cuo - pick_time_cuo <= 86400:
                            goods['score'] += 30
                        elif 86400 < time_cuo - pick_time_cuo <= 86400 * 5:
                            goods['score'] += 15
                        else:
                            goods['score'] += 5
                    elif pick_time_cuo >= time_cuo:
                        # 时间戳一天相差60*60*24=86400
                        if pick_time_cuo - time_cuo <= 86400:
                            goods['score'] += 30
                        elif 86400 < pick_time_cuo - time_cuo <= 86400 * 5:
                            goods['score'] += 15
                        else:
                            goods['score'] += 5
            # 选出最符合的物品，挑选分数最大的
            max_score_goods = max(GoodsInfo, key=lambda n: n['score'])
            max_score=str(max_score_goods['score'])[:4]
            # 根据选出分数的最大的，查找数据库中该物品的信息
            foo = Loss_goods.objects.filter(id=max_score_goods['id']).first()

    return render(request, 'user/pickup_ai.html', locals())
