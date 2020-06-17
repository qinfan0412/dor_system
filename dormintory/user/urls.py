from django.urls import path, re_path
from user import views

urlpatterns = [
    # -------------------------------注册，登录，忘记密码，登出
    path('register/', views.register),  # 注册路由
    path('register_ajax_data/', views.register_ajax_data),  # 注册返回的ajax数据
    re_path('register_ajax_data/(?P<status>\d)', views.register_ajax_data),  # 注册返回的ajax数据
    re_path('^$', views.login),  # 登陆路由
    path('login/', views.login),  # 登陆路由
    path('logout/', views.logout),  # 登出路由
    path('forgot_password/', views.forgot_password),  # 忘记密码路由
    path('forgot_password_ajax/', views.forgot_password_ajax),  # 忘记密码返回的ajax数据
    re_path('forgot_password_ajax/(?P<status>\d)', views.forgot_password_ajax),  # 忘记密码返回的ajax数据

    # ---------------------------未登录主页，登录后主页，关于我们，修改密码
    path('index1/', views.index1),  # 未登录主页路由
    path('index2/', views.index2),  # 登录后主页路由
    path('about/', views.about),  # 关于我们
    path('update_info/', views.update_info),  # 修改个人信息
    path('update_info_ajax/', views.update_info_ajax),  # 修改信息返回的ajax数据
    path('update_password/', views.update_password),  # 修改密码

    # --------------------------------------更换宿舍
    path('update_dor_form/', views.update_dor_form),  # 更换宿舍申请
    path('update_dor_history/', views.update_dor_history),  # 更换宿舍历史
    re_path('update_dor_history/(?P<del_id>\d+)', views.update_dor_history),  # 更换宿舍历史

    # -------------------------------------宿舍维修
    path('fix_dor_form/', views.fix_dor_form),  # 宿舍维修申请
    path('fix_dor_form_update/', views.fix_dor_form_update),  # 宿舍维修申请修改
    re_path('fix_dor_form_update/(?P<id>\d+)', views.fix_dor_form_update),  # 宿舍维修申请修改
    path('fix_dor_history/', views.fix_dor_history),  # 宿舍维修历史
    re_path('fix_dor_history/(?P<del_id>\d+)', views.fix_dor_history),  # 宿舍维修历史

    # ---------------------------------投诉和建议
    path('complaint/', views.complaint),  # 投诉管理员页
    path('complaint_ajax/', views.complaint_ajax),  # 投诉管理员页
    path('opinions/', views.opinions),  # 其他意见页
    path('opinions_ajax/', views.opinions_ajax),  # 其他意见页

    # ------------------------------------丢失管理
    path('goods_loss_send/', views.goods_loss_send),  # 丢失发布
    path('goods_loss_look/', views.goods_loss_look),  # 丢失信息查看
    path('goods_pickup_send/', views.goods_pickup_send),  # 拾取发布
    path('goods_pickup_look/', views.goods_pickup_look),  # 丢失信息查看
    path('goods_loss_look/', views.goods_loss_look),  # 丢失信息查看
    path('loss_ai/', views.loss_ai),  # 智能推荐疑似丢失
    path('pickup_ai/', views.pickup_ai),  # 智能推荐疑似失主
    path('goods_loss_look/', views.goods_loss_look),  # 丢失信息查看
    path('pickup_list/', views.pickup_list),  # 拾取列表
    re_path('pickup_list/(?P<page>\d+)', views.pickup_list),
    path('loss_list/', views.loss_list),  # 丢失列表
    re_path('loss_list/(?P<page>\d+)', views.loss_list),

    # -----------------------------------公告信息
    path('notice_list/', views.notice_list),  # 公告列表
    path('housemaster/', views.housemaster),  # 公告列表
    re_path('notice_look/(?P<id>\d+)', views.notice_look),  # 公告查看

]
