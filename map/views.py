from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from map.models import DiscountData
from celery_task import tasks
from celery.result import AsyncResult
# Create your views here.

import os
import time
import json
import random
import traceback
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qsl, quote

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
    tasks_list = []
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
            res=tasks.soup_page_info.delay(discount_url, master_name, card, card_name_map, discount_type)
            one_task = {
                        'master_name': master_name,
                        'discount_type': discount_type,
                        'task_id': AsyncResult(res.task_id).task_id
                    }
            tasks_list.append(one_task)
    print(type(tasks_list))
    return JsonResponse(tasks_list, safe=False)

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
        else:
            print("place: " ,one.place)
            results.append({
                "place": one.place,
                "message": f"Not find {local_file_path} in local",
                "status": "error"
            })
    return JsonResponse(results, safe=False)