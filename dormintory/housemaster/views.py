import smtplib
import hashlib
import re
import time
import random
import datetime
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
        subject = '来自宿舍管理系统的重要邮件！'  # 发送的主题，可自由填写—
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
        cookie_user_id = request.COOKIES.get('user_id')
        session_user_id = request.session.get('user_id')
        if cookie_user_id == session_user_id and cookie_user_id and session_user_id:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/housemaster/login/')

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
    return render(request, 'housemaster/register.html')


def register_ajax_data(request):
    stastus = request.GET.get('status')  # 获取按钮要操作的状态
    result = {}
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        email = request.POST.get('email')
        name = request.POST.get('user_name')
        miyao = request.POST.get('miyao')  # 秘钥
        # 发送邮箱
        if stastus == '1':
            if user_id and not User.objects.filter(user_id=user_id).first():
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
            if user_id and password and email and emailcode and name and miyao:
                # 然后数据库中没有此账户存在
                user = User.objects.filter(user_id=user_id).first()
                if not user:
                    # 不存在判断邮箱验证码是否相同，或者过了时间
                    ver = Verification.objects.filter(email=email).last()  # 查找该邮箱的最后一个验证码
                    if ver and ver.verification_code == emailcode and time.time() - ver.create_time <= 60:
                        # 判断秘钥是否正确
                        if miyao == '8888':
                            User.objects.create(password=setPassword(password), user_id=user_id, email=email, name=name)
                            result = {'code': 10000, 'content': '恭喜!账户【%s】注册成功!' % user_id}
                        else:
                            result = {'code': 10009, 'content': '提示信息:秘钥验证失败'}
                    else:
                        result = {'code': 10007, 'content': '提示信息:验证码失效或者输入错误！'}
                else:
                    result = {'code': 10005, 'content': '提示信息:账户【%s】已存在！请再想个新的账号' % user_id}
            else:
                result = {'code': 10004, 'content': '提示信息:请检查，信息还没填全！'}
    return JsonResponse(result)


# ====================================登录功能=====================================================
def login(request):
    result = {'code': 00000, 'content': random_sentence()}
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        print(user_id, password)
        # 如果账户密码都不为空
        if user_id and password:
            # 判断账户是否存在
            has_user_id = User.objects.filter(user_id=user_id).first()
            if has_user_id:
                if setPassword(password) == has_user_id.password:
                    # 密码成功就设置cookie和session
                    response = HttpResponseRedirect('/housemaster/index/')
                    response.set_cookie('user_id', user_id)
                    request.session['user_id'] = user_id
                    result['code'] = 10000
                    return response
                else:
                    result['code'] = 10003
                    result['content'] = '提示信息：密码输入错误！'

            else:
                result['code'] = 10002
                result['content'] = '提示信息:账户【%s】不存在！' % user_id

        else:
            result['code'] = 10001
            result['content'] = '提示信息:信息还没填全呦！'
    return render(request, 'housemaster/login.html', locals())


# ====================================退出登录功能=================================================
def logout(request):
    # 删除cookie和session
    response = HttpResponseRedirect('/housemaster/login/')  # 返回登录页
    del request.session['user_id']
    response.delete_cookie('user_id')  # 删除指定cookie
    response.delete_cookie('sessionid')  # 删除指定cookie
    return response


# ====================================忘记密码（ajax）=============================================
def forget_password(request):
    return render(request, 'housemaster/forgot_password.html')


def forget_password_ajax(request):
    stastus = request.GET.get('status')  # 获取按钮要操作的状态
    result = {'code': 00000, 'content': '提示信息：无'}
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        email = request.POST.get('email')
        # 发送邮箱验证码
        if stastus == '1':
            if user_id and email:
                has_user_id = User.objects.filter(user_id=user_id).first()
                if has_user_id:
                    # 判断邮箱是否正确
                    if has_user_id.email == email:
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
            if user_id and email and emailcode:
                # 判断账户是否存在
                has_user_id = User.objects.filter(user_id=user_id).first()
                if has_user_id:
                    # 判断邮箱是否正确
                    if has_user_id.email == email:
                        # 如果有幸正确，判断输入验证码是否过期或者错误
                        ver = Verification.objects.filter(email=email).last()  # 查找该邮箱的最后一个验证码
                        if ver and ver.verification_code == emailcode and time.time() - ver.create_time <= 60:
                            password = str(random.randint(10000000, 99999999))
                            has_user_id.password = setPassword(password)
                            has_user_id.save()
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


# ------------------------------------------------------首页
@LoginDescribe
def index(request):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())[:10]  # 时间日期
    change_dor_all = len(Change_dor.objects.all())  # 更换宿舍总人数
    fix_dor_all = len(Fix_dor.objects.all())  # 修理宿舍总人数
    stu_all = len(Stu.objects.all())  # 学生用户总人数
    user_all = len(User.objects.all())  # 管理员用户总人数
    notice_all = len(Notice.objects.all())  # 总公告数
    first_notice = Notice.objects.all().order_by('-id').first()
    return render(request, 'housemaster/index.html', locals())


# --------------------------------------------修改个人密码页面
@LoginDescribe
def update_password(request):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    content = '提示信息：你正在修改个人密码...修改成功后返回登录页'
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        # 必须全部填写
        if old_password and new_password1 and new_password2:
            user = User.objects.filter(user_id=user_id).first()
            password = user.password
            # 判断旧密码是否正确
            if setPassword(old_password) == password:
                # 判断两个新密码是否相同
                if new_password1 == new_password2:
                    # 判断新密码是否与旧密码相同
                    if setPassword(new_password1) != password:
                        user.password = setPassword(new_password1)
                        user.save()
                        content = '提示信息:恭喜！密码修改成功...请重新登录'
                        # 删除cookie和session
                        response = HttpResponseRedirect('/housemaster/login/')  # 返回登录页
                        del request.session['user_id']
                        response.delete_cookie('user_id')  # 删除指定cookie
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
    return render(request, 'housemaster/upadate_password.html', locals())


# ------------------------------------------个人中心页面
def user_info(request):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    name = user.name
    phone = user.phone
    email = user.email
    location = user.location
    sex = user.sex
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        user.location = request.POST.get('location')
        user.sex = request.POST.get('sex')
        user.save()

        return HttpResponseRedirect('/housemaster/user_info/')
    return render(request, 'housemaster/user_info.html', locals())


# --------------------------------------------换宿舍申请列表
def dor_update_list(request, page=1):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    # 查询换宿申请表
    change_dor = Change_dor.objects.all().order_by('-id')
    paginator = Paginator(change_dor, 6)  # 分页一页显示六条
    page_obj = paginator.page(int(page))

    # 搜索框
    search = request.GET.get('search')
    if search:
        change_dor = Change_dor.objects.filter(id__contains=search)
        if not change_dor:
            change_dor = Change_dor.objects.all().order_by('-id')
            result = '无结果！'
        else:
            paginator = Paginator(change_dor, 8)  # 分页一页显示六条
            page_obj = paginator.page(int(page))
    return render(request, 'housemaster/dor_update_list.html', locals())


# --------------------------------------------处理换宿申请页面

def dor_update_process(request):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    # 获取该申请单的信息
    id = request.GET.get('id')
    change_dor = Change_dor.objects.filter(id=int(id)).first()
    # 获取处理结果
    if request.method == "POST":
        status = request.POST.get('status')
        if status == '1':
            # 同意更换则更改换宿表状态和学生表学生宿舍
            change_dor.admin = user.name
            change_dor.status = 1
            change_dor.process_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            change_dor.save()
            stu = Stu.objects.get(stu_id=change_dor.stu_id)  # 查出学生
            # 原宿舍学生现存人数减一
            old_dor = stu.dor
            old_dor.now_people = old_dor.now_people - 1
            # 学生绑定新宿舍
            stu.dor = Dor.objects.filter(num=change_dor.go_dor).first()
            new_dor = stu.dor
            if new_dor.now_people+1 <= new_dor.max_people:
                # 新宿舍现存人数加1,并且修改所有表
                new_dor.now_people = new_dor.now_people + 1
                new_dor.save()
                stu.save()
                old_dor.save()
            else:
                content = '失败！新宿舍人数已满！只可以拒绝！'
            return HttpResponseRedirect('/housemaster/dor_update_process/?id={}'.format(id))
        elif status == '2':
            # 拒绝更换只修改换宿表状态
            change_dor.admin = user.name
            change_dor.status = 2
            change_dor.process_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            change_dor.save()
            return HttpResponseRedirect('/housemaster/dor_update_process/?id={}'.format(id))
        else:
            content = '未处理！请处理后再提交'
    return render(request, 'housemaster/dor_update_process.html', locals())


# -------------------------------------------------宿舍报修列表
def fix_dor_list(request, page=1):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    # 查询换宿申请表
    fix_dor = Fix_dor.objects.all().order_by('-id')
    paginator = Paginator(fix_dor, 8)  # 分页一页显示六条
    page_obj = paginator.page(int(page))

    # 搜索框
    search = request.GET.get('search')
    if search:
        fix_dor = Fix_dor.objects.filter(id__contains=search)
        if not fix_dor:
            fix_dor = Fix_dor.objects.all().order_by('-id')
            result = '无结果！'
        else:
            paginator = Paginator(fix_dor, 8)  # 分页一页显示六条
            page_obj = paginator.page(int(page))
    return render(request, 'housemaster/fix_dor_list.html', locals())


# --------------------------------------------处理宿舍报修页面
def fix_dor_process(request):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    id = request.GET.get('id')
    fix_dor = Fix_dor.objects.filter(id=int(id)).first()
    if request.method == "POST":
        fix_dor.admin = user.name
        fix_dor.status = 1
        fix_dor.process_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        fix_dor.save()
    return render(request, 'housemaster/fix_dor_process.html', locals())


# ----------------------------------------------公告发布页面
def notice_send(request):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    return render(request, 'housemaster/notice_send.html', locals())


def get_notice_ajax(request):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    result = {'code': 1000, 'content': ''}
    if request.method == "POST":
        title1 = request.POST.get('title1')
        content1 = request.POST.get('content1')
        if title1 and content1:
            if len(title1) >= 50:
                result = {'code': 10002, 'content': '失败！标题过长！'}
            else:
                Notice.objects.create(
                    user_id=user_id,
                    user_name=user.name,
                    title=title1,
                    content=content1,
                    send_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                    finally_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                )
                result = {'code': 10000, 'content': '恭喜！发布成功'}
        else:
            result = {'code': 10001, 'content': '失败！请填写完内容再发布'}
    return JsonResponse(result)


# ----------------------------------------------公告列表页面
def notice_list(request, page=1):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    notice = Notice.objects.all().order_by('-id')
    paginator = Paginator(notice, 8)  # 分页一页显示六条
    page_obj = paginator.page(int(page))

    # 删除公告
    del_id = request.GET.get('del_id')
    if del_id:
        del_id = int(del_id)
        Notice.objects.get(id=del_id).delete()
    # 搜索框
    search = request.GET.get('search')
    if search:
        notice = Notice.objects.filter(title__contains=search)
        if not notice:
            notice = Notice.objects.all().order_by('-id')
            result = '无结果！'
        else:
            paginator = Paginator(notice, 8)  # 分页一页显示六条
            page_obj = paginator.page(int(page))
    return render(request, 'housemaster/notice_list.html', locals())


# ----------------------------------------------公告修改页面
def notice_update(request):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    id = request.GET.get('id')
    notice = Notice.objects.get(id=id)
    result = dict()
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            if len(title) <= 50:
                notice = Notice.objects.get(id=id)
                notice.title = title
                notice.content = content
                notice.finally_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                notice.save()
                result = {'code': 10000, 'content': '恭喜！修改成功'}
            else:
                result = {'code': 10002, 'content': '失败！标题过长！'}
    else:
        result = {'code': 10001, 'content': '失败！请填写完内容再发布'}
    print(result)

    return render(request, 'housemaster/notice_update.html', locals())


# ----------------------------------------------公告查看页面
def notice_look(request):
    user_id = request.COOKIES.get('user_id')
    user = User.objects.filter(user_id=user_id).first()
    id = request.GET.get('id')
    notice = Notice.objects.get(id=id)
    return render(request, 'housemaster/notice_look.html', locals())
