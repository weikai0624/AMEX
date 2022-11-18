from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

import json
import requests
from bs4 import BeautifulSoup


def find_list_of_dict(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] in value or value in dic[key] :
            return i
    return -1


def show_map(request):
    url = "https://www.amexcards.com.tw/benefit/esavvy/"
    # r = requests.get("https://www.amexcards.com.tw/benefit/esavvy/list.aspx?card=3")
    r = requests.get("https://www.amexcards.com.tw/benefit/esavvy/detail.aspx?card=3&offer=558")

    soup = BeautifulSoup(r.text, "html.parser")

    # print(r.text)
    ## 該卡別的所有優惠方案
    # sel = soup.select("div.card a.side__btn-main.collapsed")

    dict_ = []
    sel = soup.select("div.card")
    for s in sel:
        discount_type = s.find("a").text
        for o in s.select('li a'):
            place = o.text
            if place == "【因應疫情相關通知】":
                continue
            href = o['href']
            in_dict_index = find_list_of_dict(dict_, 'place', place)
            if in_dict_index == -1:
                one={
                    "place":place,
                    "discount":[
                        {
                            "discount_type": discount_type,
                            "href": url + "/" + href
                    }
                    ],
                    "position":{
                        "longitude": 1,
                        "latitude": 2,
                    }
                }
                dict_.append(one)
            else:
                dict_[in_dict_index]['discount'].append({
                            "discount_type": discount_type,
                            "href":  url + "/" + href
                    })
    return JsonResponse(dict_, safe=False)
