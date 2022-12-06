from django.conf import settings

import requests
from copy import deepcopy
from bs4 import BeautifulSoup
from celery import shared_task
from map.models import DiscountData
from common.common import replace_space


def create_to_db(one_place):
    # 為保留 上方oneplace完整性
    one_place_data = deepcopy(one_place)
    _place = one_place_data.pop('place')
    _card = one_place_data.pop('card')
    # 優先搜尋place&card , 如有對應的則使用defaults update, 如無則 create !
    one_data, created = DiscountData.objects.update_or_create(place=_place, card=_card, defaults=one_place_data)
    return one_data, created

@shared_task
def soup_page_info(discount_url, master_name, card, card_name_map, discount_type):
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
        create_to_db(one_place)
        return one_place