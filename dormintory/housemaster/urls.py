from django.urls import path, re_path
from housemaster import views

urlpatterns = [
    # 注册
    path('register/', views.register),  # 注册路由
    path('register_ajax_data/', views.register_ajax_data),  # 注册返回的ajax数据
    re_path('register_ajax_data/(?P<status>\d)', views.register_ajax_data),  # 注册返回的ajax数据
    # 登录，登出
    re_path('^$', views.login),  # 登陆路由
    path('login/', views.login),  # 登陆路由
    path('logout/', views.logout),  # 登出路由
    # 忘记密码
    path('forget_password/', views.forget_password),  # 忘记密码路由
    path('forget_password_ajax/', views.forget_password_ajax),  # 忘记密码返回的ajax数据
    re_path('forget_password_ajax/(?P<status>\d)', views.forget_password_ajax),  # 忘记密码返回的ajax数据
    #   主页
    path('index/', views.index),
    # 个人密码，个人中心
    path('update_password/', views.update_password),
    path('user_info/', views.user_info),
    # 宿舍更换
    path('dor_update_process/', views.dor_update_process),
    re_path('dor_update_list/(?P<page>\d+)', views.dor_update_list),
    # 宿舍报修
    re_path('fix_dor_list/(?P<page>\d+)', views.fix_dor_list),
    path('fix_dor_process/', views.fix_dor_process),
    # 公告
    path('notice_send/', views.notice_send),
    path('get_notice_ajax/', views.get_notice_ajax),
    path('notice_list/', views.notice_list),
    re_path('notice_list/(?P<page>\d+)', views.notice_list),
    path('notice_update/', views.notice_update),
    path('notice_look/', views.notice_look),

]
