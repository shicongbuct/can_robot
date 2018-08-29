from django.shortcuts import render, render_to_response
from deps import itchat as Itchat

import time
import base64
import uuid
import json
import datetime
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
login_info = {}

def index(request):
    print('start to request')
    if request.GET.get('pwd') != u'can123':
        return HttpResponse("密码错误")
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
        resp = {"isLogin": False}
        return HttpResponse(json.dumps(resp), content_type="application/json")
    chat = chat_obj.get("chat")
    login_info = chat.get_login_info()
    nick_name = login_info.get("User").get("NickName")
    chat_dict[chat_id]["nick_name"] = nick_name
    print(nick_name)
    resp = {"isLogin": True, "nickName": nick_name, "chat_id": chat_id}
    return HttpResponse(json.dumps(resp), content_type="application/json")

def formatPrice(msg, price):
    resText = "非小号的" + msg['Text'].lower() + "价格: " + price.get("price", "未成功获取") + "\n"
    resText += "涨幅: " + price.get("change") + "\n"
    resText += "24h成交额: " + price.get("balanceVolume") + "\n"
    if price.get("rank"):
        resText += "市值排名： " + price.get("rank") + "\n"
    if price.get("website"):
        resText += "更多： http:" + price.get("website") + "\n"
    resText += "时间： " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return resText

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
        if msg['Text'].lower() in (u'can', u'币价'):
            price = model.fetchPrice('can', '/currencies/can/')
            return formatPrice(msg, price)
        if st.index_dict.get(msg['Text'].lower()):
            price = model.fetchPrice(msg['Text'].lower(), st.index_dict.get(msg['Text'].lower()))
            return formatPrice(msg, price)

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
    chat_obj = get_chat_instance(request.COOKIES["can_robot"])
    chat_obj.get("chat").send_image(file_ = upload_file, toUserName = 'filehelper')
    return HttpResponse("ok")

def mult_msg(request):
    chat_obj = get_chat_instance(request.COOKIES["can_robot"])
    chat = chat_obj.get("chat")
    message = request.POST.get("text")
    chat_room_list = chat.get_chatrooms()
    for chat_room in chat_room_list:
        userName = chat_room.get("UserName")
        chat.send_msg(msg=message, toUserName= userName)
    return HttpResponse("ok")

def mult_image(request):
    chat_obj = get_chat_instance(request.COOKIES["can_robot"])
    chat = chat_obj.get("chat")
    upload_file = request.FILES.get("muli_image_file")
    chat_room_list = chat.get_chatrooms()
    for chat_room in chat_room_list:
        userName = chat_room.get("UserName")
        chat.send_image(file_=upload_file, toUserName=userName)
    return HttpResponse("ok")

# def send_share_msg(request):
#     chat_obj = get_chat_instance(request.COOKIES["can_robot"])
#     chat = chat_obj.get("chat")
#     #share_url = 'https://mp.weixin.qq.com/s/TNycTpMIpz3vIjihfOz5Uw'
#     #share_url = request.POST.get("url")
#     content = '<msg><appmsg appid="" sdkver="0"><title>十城链欢丨币世界携手CAN开启周年狂欢庆！</title><des>CAN携手币世界开启周年狂欢庆典！</des><username></username><action>view</action><type>5</type><showtype>0</showtype><content></content><url>http://mp.weixin.qq.com/s?__biz=MzI1ODU1ODcyOA==&amp;mid=2247484784&amp;idx=1&amp;sn=3621e39f902192b4887087dde499863f&amp;chksm=ea071b17dd70920188e8f879c0cdd458d782ceee4a329b24fca896e0f46e1ef89e7b2835446d&amp;mpshare=1&amp;scene=1&amp;srcid=0820Pb0enMafUxYt1noYXdQm#rd</url><lowurl></lowurl><dataurl></dataurl><lowdataurl></lowdataurl><contentattr>0</contentattr><streamvideo><streamvideourl></streamvideourl><streamvideototaltime>0</streamvideototaltime><streamvideotitle></streamvideotitle><streamvideowording></streamvideowording><streamvideoweburl></streamvideoweburl><streamvideothumburl></streamvideothumburl><streamvideoaduxinfo></streamvideoaduxinfo><streamvideopublishid></streamvideopublishid></streamvideo><canvasPageItem><canvasPageXml><![CDATA[]]></canvasPageXml></canvasPageItem><appattach><attachid></attachid><cdnthumburl>305a020100045330510201000204482ce19902033d0af802049030feb602045b7a54ab042c6175706170706d73675f613131383162653863373837653430655f313533343734333732323838315f3132340204010400030201000400</cdnthumburl><cdnthumbmd5>a94eefecc47c472b7c1bd46c42aa334f</cdnthumbmd5><cdnthumblength>19206</cdnthumblength><cdnthumbheight>68</cdnthumbheight><cdnthumbwidth>120</cdnthumbwidth><cdnthumbaeskey>63de0e1d594749d9842e8df4501e7117</cdnthumbaeskey><aeskey>63de0e1d594749d9842e8df4501e7117</aeskey><encryver>1</encryver><fileext></fileext><islargefilemsg>0</islargefilemsg></appattach><extinfo></extinfo><androidsource>2</androidsource><sourceusername></sourceusername><sourcedisplayname>5UWiFi</sourcedisplayname><commenturl></commenturl><thumburl></thumburl><mediatagname></mediatagname><messageaction><![CDATA[]]></messageaction><messageext><![CDATA[]]></messageext><emoticongift><packageflag>0</packageflag><packageid></packageid></emoticongift><emoticonshared><packageflag>0</packageflag><packageid></packageid></emoticonshared><designershared><designeruin>0</designeruin><designername>null</designername><designerrediretcturl>null</designerrediretcturl></designershared><emotionpageshared><tid>0</tid><title>null</title><desc>null</desc><iconUrl>null</iconUrl><secondUrl>null</secondUrl><pageType>0</pageType></emotionpageshared><webviewshared><shareUrlOriginal>http://mp.weixin.qq.com/s?__biz=MzI1ODU1ODcyOA==&amp;mid=2247484784&amp;idx=1&amp;sn=3621e39f902192b4887087dde499863f&amp;chksm=ea071b17dd70920188e8f879c0cdd458d782ceee4a329b24fca896e0f46e1ef89e7b2835446d&amp;scene=0#rd</shareUrlOriginal><shareUrlOpen>https://mp.weixin.qq.com/s?__biz=MzI1ODU1ODcyOA==&amp;mid=2247484784&amp;idx=1&amp;sn=3621e39f902192b4887087dde499863f&amp;chksm=ea071b17dd70920188e8f879c0cdd458d782ceee4a329b24fca896e0f46e1ef89e7b2835446d&amp;scene=0&amp;ascene=7&amp;devicetype=android-23&amp;version=26060739&amp;nettype=WIFI&amp;abtest_cookie=AwABAAoACwASAAMAJZceADuZHgBImR4AAAA=&amp;lang=zh_CN&amp;pass_ticket=4sK/Rj4vLc2Q+jxpapkl3WfFCuj0664QlY6Fbzpq493Gk76MqPJSydk5zP0KIe4z&amp;wx_header=1</shareUrlOpen><jsAppId></jsAppId><publisherId>msg_2974769739368062507</publisherId></webviewshared><template_id></template_id><md5>a94eefecc47c472b7c1bd46c42aa334f</md5><weappinfo><username></username><appid></appid><appservicetype>0</appservicetype></weappinfo><statextstr></statextstr><websearch><rec_category>0</rec_category></websearch></appmsg><fromusername></fromusername><scene>0</scene><appinfo><version>1</version><appname></appname></appinfo><commenturl></commenturl></msg>',
#
#     chat.send_raw_msg(msgType= Itchat.content.SHARING, content= content, toUserName= 'filehelper')
#     return HttpResponse("ok")

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
