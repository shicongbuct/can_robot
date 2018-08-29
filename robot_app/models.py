from django.db import models
import requests
import datetime
import re
import time
from django.utils import timezone

# Create your models here.

def fetchPrice(key, value):
    url = 'https://www.feixiaohao.com' + value
    r = requests.get(url)
    price = re.search(r'<div class=coinprice>(.*?)<', r.text, re.M | re.I).group(1)
    balanceVolume = re.search(r'<div class=tit>24H成交额</div><div class=value>(.*?)<', r.text, re.M | re.I).group(1)
    change = re.search(r'<div class=coinprice>.*?<span class=tags-.*?>(.*?)</span><', r.text, re.M | re.I).group(1)
    rank = re.search(r'<span class=tag-marketcap>(.*?)<', r.text, re.M | re.I)
    website = re.search(r'网站：</span><span class=value> <a href="(.*?)" rel=nofollow target=_blank>网站1</a>', r.text, re.M | re.I)
    if rank:
        rank = rank.group(1)
    if website:
        website = website.group(1)
        if not website.startswith("http"):
            website = "http:" + website
    return {
        "price": price,
        "balanceVolume": balanceVolume,
        "change": change,
        "rank": rank,
        "website": website
    }

# def fetchCanPrice():
#     r = requests.get('https://www.feixiaohao.com/currencies/can/')
#     print(r)
#     price = re.search(r'<div class=coinprice>(.*?)<', r.text, re.M | re.I).group(1)
#     balanceVolume = re.search(r'<div class=tit>24H成交额</div><div class=value>(.*?)<', r.text, re.M | re.I).group(1)
#     return {
#         "price" : price,
#         "balanceVolume" : balanceVolume
#     }

class Keyword(models.Model):
    """
    关键词列表
    """

    keyword = models.CharField(default="", max_length=30, verbose_name="关键词", help_text="关键词")
    desc = models.TextField(default="", verbose_name="回复信息", help_text="回复信息")
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "关键词信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.keyword


