from django.shortcuts import render, render_to_response
from deps import itchat as Itchat

import time
import base64
import uuid
from robot_app import static_text as st
import robot_app.models as model
from .models import Keyword

# Create your views here.
from django.http import HttpResponse

'''
    chat_id : {
        chat: ${chat},
        create_Time: ${create_Time},
        isLogin: false
    }
'''
chat_dict = {}

def index(request):
    print('start to request')
    delete_unused_chat(9)
    chat = Itchat.new_instance()
    qrStorage = chat.download_Qrcode()
    chat_id = uuid.uuid1()
    chat_dict[str(chat_id)] = {"chat": chat, "create_Time": time.time(), "isLogin": False}

    context = {
        'qrStorage': base64.b64encode(qrStorage).decode('utf-8'),
    }
    response = render_to_response('login.html', context)
    response.set_cookie('can_robot', chat_id)
    return response

def get_chat_dict_num(request):
    return HttpResponse(str(len(chat_dict)) + " ---- ")

def check_login(request):
    chat_id = request.COOKIES["can_robot"]
    chat_obj = get_chat_instance(chat_id)
    if not chat_obj:
        return HttpResponse("error: not has this chat_id")
    if not chat_obj.get("isLogin"):
        return HttpResponse("notLogin")
    return HttpResponse("hasLogin")

def run(request):
    chat_id = request.COOKIES["can_robot"]
    chat_obj = get_chat_instance(chat_id)
    chat = chat_obj.get("chat", "")
    chat_dict[chat_id]["isLogin"] = True

    # check if user has scan qrcode
    status = chat.check_login()
    if status != '200':
        return HttpResponse('notScan')

    @chat.msg_register(Itchat.content.TEXT)
    def reply_test(msg):
        if msg['Text'] in (u'can', u'币价'):
            price = model.fetchPrice()
            return "当前币价为：" + price.get("price", "未成功获取") + "\n24h成交额为：" + price.get("balanceVolume", "未成功获取")

        for item in Keyword.objects.all():
            if item.keyword == msg['Text']:
                return item.desc

        return st.default_replay

    chat.loading()
    chat.run()
    del chat_dict[chat_id]
    return HttpResponse('hasLogout')

def send_page(request):
    chat_id = request.GET.get('chat_id')
    response = render_to_response('send.html')
    response.set_cookie('can_robot', chat_id)
    return response

def send_pic(request):
    upload_file = request.FILES.get("image_file")
    with open("images/" + upload_file.name, "wb") as f:
        f.write(upload_file.read())
    chat_obj = get_chat_instance(request.COOKIES["can_robot"])
    if not chat_obj:
        return HttpResponse('error, not find chat_id')
    with open("images/" + upload_file.name, 'rb') as f:
        chat_obj.get("chat").send_image(file_ = f, toUserName = 'filehelper')
    return HttpResponse("ok")

def delete_unused_chat(limit_num):
    # delete unused chat instance
    if len(chat_dict) > limit_num:
        del_list = []
        for key, value in chat_dict.items():
            if not value.get("isLogin", ""):
                del_list.append(key)
        for key in del_list:
            del chat_dict[key]

def get_chat_instance(chat_id):
    chat_obj = chat_dict.get(chat_id, "")
    if not chat_obj :
        return HttpResponse('error, not find chat_id')
    return chat_obj