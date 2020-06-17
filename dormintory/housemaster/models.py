from user.models import *
from django.db import models
from ckeditor.fields import RichTextField


# ------------------------------------------------------邮箱验证码表
class Verification(models.Model):
    email = models.CharField(max_length=32, verbose_name='邮箱')
    verification_code = models.CharField(max_length=32, verbose_name='验证码')
    create_time = models.IntegerField(verbose_name='创办时间')

    class Meta:
        db_table = 'Verification'
        verbose_name = '验证码表'
        verbose_name_plural = verbose_name


# ------------------------------------------------------------宿舍表
class Dor(models.Model):
    num = models.CharField(verbose_name='宿舍号', max_length=32, unique=True)
    sex = models.CharField(verbose_name='居住性别', max_length=32)
    max_people = models.IntegerField(verbose_name='最大人数')
    now_people = models.IntegerField(verbose_name='现在人数')

    class Meta:
        db_table = 'Dor'
        verbose_name = '宿舍表'
        verbose_name_plural = verbose_name


# -------------------------------------------------------------管理员用户表
class User(models.Model):
    user_id = models.CharField(max_length=32, verbose_name='账号', unique=True)
    password = models.CharField(max_length=32, verbose_name='密码')
    email = models.CharField(max_length=32, verbose_name='邮箱')  # 用于忘记密码功能
    name = models.CharField(max_length=32, verbose_name='姓名')
    phone = models.CharField(max_length=32, verbose_name='电话', default='0000000000')
    location = models.CharField(max_length=32, verbose_name='住址', default='地球')
    sex = models.CharField(verbose_name='性别', max_length=32, default='男生')

    class Meta:
        db_table = 'User'
        verbose_name = '管理员用户表'
        verbose_name_plural = verbose_name


# -------------------------------------------------------------------------学生用户表
class Stu(models.Model):
    stu_id = models.CharField(max_length=32, verbose_name='账号', unique=True)
    password = models.CharField(max_length=32, verbose_name='密码')
    email = models.CharField(max_length=32, verbose_name='邮箱')  # 用于忘记密码功能
    name = models.CharField(max_length=32, verbose_name='姓名')
    phone = models.CharField(max_length=32, verbose_name='电话', default='0')
    major_class = models.CharField(max_length=32, default='未知', verbose_name='专业班级')
    birthday = models.CharField(verbose_name='出生日期', max_length=32, default='2000-01-01')
    remarks = models.CharField(max_length=256, verbose_name='备注', default='无')
    sex = models.CharField(verbose_name='性别', max_length=32)
    dor = models.ForeignKey(to=Dor, to_field='num', on_delete=models.CASCADE, verbose_name='宿舍号', null=True)

    class Meta:
        db_table = 'Stu'
        verbose_name = '学生用户表'
        verbose_name_plural = verbose_name


# -------------------------------------------------------------------------更换宿舍申请表
class Change_dor(models.Model):
    stu_id = models.CharField(max_length=32, verbose_name='申请账号')
    name = models.CharField(max_length=32, verbose_name='姓名')
    sex = models.CharField(verbose_name='性别', max_length=32)
    major_class = models.CharField(max_length=32, default='未知', verbose_name='专业班级')
    now_dor = models.CharField(max_length=32, verbose_name='更换前宿舍')
    go_dor = models.CharField(max_length=32, verbose_name='更换至宿舍')
    remarks = models.CharField(max_length=256, verbose_name='备注', default='无')
    send_time = models.CharField(max_length=32, verbose_name='发布时间')
    admin = models.CharField(max_length=32, verbose_name='批改管理员', null=True)
    process_time = models.CharField(max_length=32, verbose_name='批改时间', null=True)
    status = models.IntegerField(verbose_name='是否同意', default=0)  # 同意为1，不同意为2,未处理为0

    class Meta:
        db_table = 'Change_dor'
        verbose_name = '更换宿舍申请表'
        verbose_name_plural = verbose_name


# -------------------------------------------------------------------------宿舍维修申请表
class Fix_dor(models.Model):
    stu_id = models.CharField(max_length=32, verbose_name='申请账号')
    name = models.CharField(max_length=32, verbose_name='姓名')
    phone = models.CharField(verbose_name='电话', max_length=32)
    dor = models.CharField(max_length=32, verbose_name='宿舍')
    simple_remarks = models.CharField(max_length=256, verbose_name='简要原因', default='无')
    detail_remarks = models.CharField(max_length=256, verbose_name='详细原因', default='无')
    send_time = models.CharField(max_length=32, verbose_name='发布时间')
    admin = models.CharField(max_length=32, verbose_name='批改管理员', null=True)
    process_time = models.CharField(max_length=32, verbose_name='批改时间', null=True)
    status = models.IntegerField(verbose_name='是否同意', default=0)  # 未处理为0，处理为1

    class Meta:
        db_table = 'Fix_dor'
        verbose_name = '宿舍维修申请表'
        verbose_name_plural = verbose_name


# -------------------------------------------------------------------------公告表
class Notice(models.Model):
    user_id = models.CharField(max_length=32, verbose_name='发布账号')
    user_name = models.CharField(max_length=32, verbose_name='姓名')
    title = models.CharField(max_length=20, verbose_name='标题')
    content = RichTextField()
    send_time = models.CharField(max_length=32, verbose_name='发布时间')
    finally_time = models.CharField(max_length=32, verbose_name='最后更新时间')

    class Meta:
        db_table = 'Notice'
        verbose_name = '公告表'
        verbose_name_plural = verbose_name


# -------------------------------------------------------------丢失物品信息表
class Loss_goods(models.Model):
    stu_id = models.CharField(max_length=32, verbose_name='丢失账号')
    loss_name = models.CharField(max_length=32, verbose_name='姓名')
    loss_phone = models.CharField(max_length=32, verbose_name='电话')
    loss_goods_name = models.CharField(max_length=32, verbose_name='丢失物品名字')
    loss_type = models.CharField(max_length=32, verbose_name='丢失类别')
    loss_location = models.CharField(max_length=32, verbose_name='丢失地点')
    loss_picture = models.ImageField(upload_to='images', verbose_name='丢失照片')
    loss_remarks = models.CharField(max_length=256, verbose_name='丢失备注', default='无')
    loss_time = models.CharField(max_length=32, verbose_name='丢失时间')
    send_time = models.CharField(max_length=32, verbose_name='订单发布时间')
    complete_time = models.CharField(max_length=32, verbose_name='订单完成时间',null=True)
    status = models.IntegerField(verbose_name='订单状态', default=0)  # 未处理为0，已找到为1

    class Meta:
        db_table = 'Loss_goods'
        verbose_name = '丢失物品信息表'
        verbose_name_plural = verbose_name

# -------------------------------------------------------------拾取物品信息表
class Pickup_goods(models.Model):
    stu_id = models.CharField(max_length=32, verbose_name='拾取账号')
    pickup_name = models.CharField(max_length=32, verbose_name='姓名')
    pickup_phone = models.CharField(max_length=32, verbose_name='电话')
    pickup_goods_name = models.CharField(max_length=32, verbose_name='拾取物品名字')
    pickup_type = models.CharField(max_length=32, verbose_name='拾取类别')
    pickup_location = models.CharField(max_length=32, verbose_name='拾取地点')
    pickup_picture = models.ImageField(upload_to='images', verbose_name='拾取照片')
    pickup_remarks = models.CharField(max_length=256, verbose_name='拾取备注', default='无')
    pickup_time = models.CharField(max_length=32, verbose_name='拾取时间')
    send_time = models.CharField(max_length=32, verbose_name='订单发布时间')
    status = models.IntegerField(verbose_name='订单状态', default=0)  # 未处理为0，已找到为1

    class Meta:
        db_table = 'Pickup_goods'
        verbose_name = '拾取物品信息表'
        verbose_name_plural = verbose_name
