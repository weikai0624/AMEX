from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from map.models import DiscountData
from celery_task import tasks
from celery.result import AsyncResult
import googlemaps
# Create your views here.

import os
import time
import json
import random
import traceback
import requests
from copy import deepcopy
from bs4 import BeautifulSoup
from common.common import find_google_map_url
from urllib.parse import urlparse, parse_qsl, quote


def create_data(request):
    card_name_map={
    '3': {
        'chinese':'信用白金卡',
        'english':'grcc-platinum'
        }
    }
    # card = int( request.GET.get('card',3) )
    card = 3
    card_name = card_name_map[str(card)]['chinese']
    card_english_name = card_name_map[str(card)]['english']
    base_url = "https://www.americanexpress.com"
    r = requests.get(f"https://www.americanexpress.com/zh-tw/benefits/annual/{card_english_name}/")
    soup = BeautifulSoup(r.text, "html.parser")

    tasks_list = []
    select_discount_type = soup.select("div.image-wrap")
    discount_types_list = []
    ## 依照優惠方案分類
    for s in select_discount_type:
        # 優惠方案
        href = s.find("a").get('href','')
        discount_type = s.find("img").get('title','')
        discount_types_list.append(discount_type)
        discount_type_url = base_url+href
        r_one_discount_type = requests.get(discount_type_url)
        soup_page = BeautifulSoup(r_one_discount_type.text, "html.parser")
        # 根據頁面中的店家進行分類
        # https://www.americanexpress.com/zh-tw/benefits/annual/grcc-platinum/dining.html
        store_info_list = soup_page.select("div.card")
        keys = []
        other_keys = []
        for s in store_info_list:
            master_name = s.select_one('h3').text.split(". ")[-1]
            # 因tasks 不能使用bs4.element.Tag 直接傳輸, 所以先經過prettify 轉換成html 再由tasks去parse 一次
            res = tasks.soup_store_info.delay(s.prettify(), master_name ,base_url, discount_type, discount_type_url, card, card_name, card_english_name)
            one_task = {
                    'master_name': master_name,
                    'discount_type': discount_type,
                    'task_id': AsyncResult(res.task_id).task_id
                }
            tasks_list.append(one_task)
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


def create_coordinate_data_google_api(request):
    results = []
    card = int( request.GET.get('card',3) )
    discount_dict_list_no_coordinate = DiscountData.objects.filter(longitude=None, latitude=None, card=card)
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAP_API_KEY)
    for one in discount_dict_list_no_coordinate:
        try:
            address = one.address
            if address == ''  :
                print('Bye', one.place, '  No address' )
                continue
            geocode_result = gmaps.geocode(address)
            
            latitude = geocode_result[0]['geometry']['location']['lat']
            longitude = geocode_result[0]['geometry']['location']['lng']
            
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
