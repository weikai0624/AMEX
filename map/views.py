from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

import json
import requests
from bs4 import BeautifulSoup




# def show_map(request):
base_url = "https://www.amexcards.com.tw/benefit/esavvy/"
r = requests.get("https://www.amexcards.com.tw/benefit/esavvy/list.aspx?card=3")
# r = requests.get("https://www.amexcards.com.tw/benefit/esavvy/detail.aspx?card=3&offer=558")

soup = BeautifulSoup(r.text, "html.parser")

# print(r.text)
## 該卡別的所有優惠方案
# sel = soup.select("div.card a.side__btn-main.collapsed")

dict_ = []
select_discount_type = soup.select("div.card")

discount_types_list = []

def replace_space(string):
    return string.replace(" ","").replace("\r", "").replace("\n", "")

def show_map(request):
    ## 依照優惠方案分類
    for s in select_discount_type:
        ## 優惠方案 
        discount_type = s.find("a").text
        discount_types_list.append(discount_type)
        ## 地點
        for o in s.select('li a'):
            place = o.text
            if place == "【因應疫情相關通知】":
                continue
            # if place != "胡同燒肉":
            #     continue
            href = o.get('href','')
            discount_url = base_url+href
            r_one_place_page = requests.get(discount_url)
            soup_page = BeautifulSoup(r_one_place_page.text, "html.parser")

            ## 根據頁面中下方商店分店進行紀錄  https://www.amexcards.com.tw/benefit/esavvy/detail.aspx?card=3&offer=540#
            detail_info_list = soup_page.select("div.detail__info")

            ## 根據每項分店
            for detail in detail_info_list:
                detail_info_one = detail.select("div.detail__info-text")
                address = ""
                place_web_url = ""
                phone = ""
                # 分析是地址or 網址or 電話
                for i in detail_info_one :
                    label = i.find("label")
                    if label is None:
                        place = replace_space(i.text)
                        print("店名:",place)
                    else:
                        label_text = label.text
                        if label_text == "地　　址：":
                            address = replace_space(i.find("a").text)
                            print("address: ",address)
                        if label_text == "網　　址：":
                            place_web_url = i.find("a").get('href','')
                            print("place_web_url: ", place_web_url)
                        if label_text == "電話預訂：":
                            # 去除<label>電話預訂：</label>
                            i.find('label').decompose()
                            phone = replace_space(i.text)
                            print("phone: ", phone)
                    ## 分店為各一處位置
                one_place={
                    "place":place,
                    "discount_type": discount_type,
                    "discount_url": discount_url ,
                    "place_web_url": place_web_url,
                    "phone": phone,
                    "address": address
                }
                dict_.append(one_place)
    return JsonResponse(dict_, safe=False)