from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

# Create your views here.

import os
import time
import json
import random
import traceback
import requests
from copy import deepcopy
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qsl



def replace_space(string):
    return string.replace(" ","").replace("\r", "").replace("\n", "")

def add_coordinate(discount_dict_list):
    base_google_search_url = "https://www.google.com/maps/place?q="
    for one in discount_dict_list:
        try:
            second = random.randint(6,20)
            print(second)
            time.sleep(second)
            address = one.get('address','')
            if address == ''  :
                print('Bye', one['place'], '  No address' )
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
            one.update({
                "longitude":longitude,
                "latitude": latitude
            })
        except:
            print("place: " ,one.get('place',''))
            print(traceback.format_exc())
    return discount_dict_list

def create_map(request):
    base_url = "https://www.amexcards.com.tw/benefit/esavvy/"
    r = requests.get("https://www.amexcards.com.tw/benefit/esavvy/list.aspx?card=3")
    # r = requests.get("https://www.amexcards.com.tw/benefit/esavvy/detail.aspx?card=3&offer=558")

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
                address = ""
                place_web_url = ""
                phone = ""
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
                one_place={
                    "place":place,
                    "discount_type": discount_type,
                    "discount_url": discount_url ,
                    "place_web_url": place_web_url,
                    "phone": phone,
                    "address": address,
                    "longitude":'',
                    "latitude": ''
                }
                discount_dict_list.append(one_place)
    

    show_map_json_path = os.path.join("D:\\AMEX\\", 'discount_dict_list_.json')
    # show_map_json = os.path.join(settings.BASE_DIR, 'AMEX_discount_dict_list.json')
    with open (file=show_map_json_path, mode='w', encoding="UTF-8") as F:
        json.dump( discount_dict_list, F, indent=4)

    discount_dict_list_add_coordinate = add_coordinate(discount_dict_list)
    show_map_json_path = os.path.join("D:\\AMEX\\", 'AMEX_discount_dict_list.json')
    # show_map_json = os.path.join(settings.BASE_DIR, 'discount_dict_list_add_coordinate.json')
    with open (file=show_map_json_path, mode='w', encoding="UTF-8") as F:
        json.dump( discount_dict_list_add_coordinate, F, indent=4)

    # return JsonResponse(discount_dict_list, safe=False)


create_map('')