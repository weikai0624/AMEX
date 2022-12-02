from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from map.models import DiscountData

# Create your views here.

import os
import time
import json
import random
import traceback
import requests
from copy import deepcopy
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qsl, quote



def replace_space(string):
    return string.replace(" ","").replace("\r", "").replace("\n", "")

def find_google_map_url(place, address):
    base_google_search_url = "https://www.google.com/maps/place?q="
    place_quote =  quote(place.encode('utf8'))
    address_quote = address
    query_quote = place_quote + " " +address_quote
    return base_google_search_url+query_quote

def create_data(request):
    card_name_map={
    '1': 'Centurion卡', 
    '2': '簽帳白金卡', 
    '3': '信用白金卡',
    '4': '簽帳金卡', 
    '6': '長榮航空簽帳白金卡',  
    '7': '晶華珍饌信用白金卡', 
    '8': '長榮航空簽帳金卡', 
    '9': '尊榮會員簽帳金卡', 
    '10': '商務金卡', 
    '11': '信用金卡', 
    '12': '簽帳卡', 
    '13': '國泰航空信用卡', 
    '14': '國泰航空尊尚信用卡', 
    '16': '商務卡'
    }
    card = int( request.GET.get('card',3) )
    base_url = "https://www.amexcards.com.tw/benefit/esavvy/"
    r = requests.get(f"https://www.amexcards.com.tw/benefit/esavvy/list.aspx?card={card}")
    soup = BeautifulSoup(r.text, "html.parser")
    discount_dict_list = []
    select_discount_type = soup.select("div.card")
    discount_types_list = []
    ## 依照優惠方案分類
    for s in select_discount_type:
        ## 優惠方案 
        discount_type = s.find("a").text
        discount_types_list.append(discount_type)
        ## 地點
        for o in s.select('li a'):
            master_name = o.text
            if master_name == "【因應疫情相關通知】":
                continue
            # if master_name != "胡同燒肉":
            #     continue
            href = o.get('href','')
            discount_url = base_url+href
            r_one_place_page = requests.get(discount_url)
            soup_page = BeautifulSoup(r_one_place_page.text, "html.parser")

            ## 根據頁面中下方商店分店進行紀錄  https://www.amexcards.com.tw/benefit/esavvy/detail.aspx?card=3&offer=540#
            detail_info_list = soup_page.select("div.detail__info")

            ## 根據每項條列的分店
            for index in range(len(detail_info_list)):
                # 如果有多家分店, 第一項為空值 , 不須帶入
                # 如果僅有一家, 第一項為資訊, 就不會有分店
                if index == 0:
                    if len(detail_info_list) > 1:
                        continue
                    else :
                        place = master_name
                # place = master_name
                detail_info_one = detail_info_list[index].select("div.detail__info-text")
                phone = ""
                address = ""
                place_web_url = ""
                google_map_url = ""
                # 分析是地址or 網址or 電話
                for i in detail_info_one :
                    label = i.find("label")
                    if label is None:
                        branch_place_name = replace_space(i.text)
                        place = master_name + "-" + branch_place_name
                        # print("店名:",place)
                    else:
                        label_text = label.text
                        if label_text == "地　　址：":
                            address = replace_space(i.find("a").text)
                            # print("address: ",address)
                        if label_text == "網　　址：":
                            place_web_url = i.find("a").get('href','')
                            # print("place_web_url: ", place_web_url)
                        if label_text == "電話預訂：":
                            # 去除<label>電話預訂：</label>
                            i.find('label').decompose()
                            phone = replace_space(i.text)
                            # print("phone: ", phone)
                ## 分店為各一處位置
                print("店名:",place)
                print("address: ",address)
                print("place_web_url: ", place_web_url)
                print("phone: ", phone)
                google_map_url = find_google_map_url(place,address)
                one_place={
                    "place": place,
                    "card": card,
                    "card_name": card_name_map[str(card)],
                    "discount_type": discount_type,
                    "discount_url": discount_url ,
                    "place_web_url": place_web_url,
                    "phone": phone,
                    "address": address
                }
                discount_dict_list.append(one_place)
                # 為保留 上方oneplace完整性
                _place = one_place.pop('place')
                _card = one_place.pop('card')
                # 優先搜尋place&card , 如有對應的則使用defaults update, 如無則 create !
                one_data, created = DiscountData.objects.update_or_create(place=_place, card=_card, defaults=one_place)
    return JsonResponse(discount_dict_list, safe=False)

def create_coordinate_data(request):
    results = []
    card = int( request.GET.get('card',3) )
    discount_dict_list_no_coordinate = DiscountData.objects.filter(longitude=None, latitude=None, card=card)
    base_google_search_url = "https://www.google.com/maps/place?q="
    for one in discount_dict_list_no_coordinate:
        try:
            second = random.randint(3,15)
            print(second)
            time.sleep(second)
            address = one.address
            if address == ''  :
                print('Bye', one.place, '  No address' )
                continue
            search_address_url = base_google_search_url+address
            r_one_place_page = requests.get(search_address_url)
            soup_page = BeautifulSoup(r_one_place_page.text, "html.parser")
            soup_page_coordinate_string = soup_page.find('head').find('meta', attrs={"itemprop":"image"})['content']
            map_url = urlparse(soup_page_coordinate_string)
            query_dict=dict(parse_qsl(map_url.query))
            lola_string = query_dict.get('center','')
            if lola_string != '':
                lalo_split = lola_string.split(',')
                latitude = float(lalo_split[0])
                longitude = float(lalo_split[1])
            
            one.longitude=longitude
            one.latitude=latitude
            one.google_map_url=find_google_map_url(one.place, one.address)

            results.append({
                "place": one.place,
                "message": "Success update longitude and latitude info, Please check google url by your self.",
                "status": "success"
            })
            one.save()
            print('succesful:', one.place)
        except:
            print("place: " ,one.place)
            print(traceback.format_exc())
            results.append({
                "place": one.place,
                "message": traceback.format_exc(),
                "status": "error"
            })
            
    return JsonResponse(results, safe=False)

def create_coordinate_data_local(request):
    results = []
    data_json_dir = os.path.join(os.path.join(settings.BASE_DIR, "map", "discount_json"))
    card = int( request.GET.get('card',3) )
    discount_dict_list_no_coordinate = DiscountData.objects.filter(longitude=None, latitude=None, card=card)
    for one in discount_dict_list_no_coordinate:
        local_file_name = one.place+'.json'
        local_file_path = os.path.join(data_json_dir, local_file_name)
        if os.path.exists(local_file_path):
            with open(os.path.join(local_file_path), 'r', encoding='utf8') as F:
                one_local_file_data = json.load(F)
            one.longitude=one_local_file_data['longitude']
            one.latitude=one_local_file_data['latitude']
            one.google_map_url=find_google_map_url(one.place, one.address)
            results.append({
                "place": one.place,
                "message": "Success update longitude and latitude info, Please check google url by your self.",
                "status": "success"
            })
            one.save()
        # else:
        #     print("place: " ,one.place)
        #     results.append({
        #         "place": one.place,
        #         "message": f"Not find {local_file_path} in local",
        #         "status": "error"
        #     })
    return JsonResponse(results, safe=False)