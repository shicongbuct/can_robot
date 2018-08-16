from django.urls import path

from . import views

urlpatterns = [
    path('login', views.index, name='index'),
    path('send_page', views.send_page, name="send_page"),
    path('get_chat_dict_num', views.get_chat_dict_num, name='get_chat_dict_num'),
    path('run', views.run, name="run"),
    path('check_login', views.check_login, name="check_login"),
    path('send_pic', views.send_pic, name="send_pic")
]