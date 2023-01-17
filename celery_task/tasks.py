from django.conf import settings
import requests
from copy import deepcopy
from bs4 import BeautifulSoup
from celery import shared_task
from map.models import DiscountData
from common.common import replace_space, find_google_map_url


def create_to_db(one_place):
    # 為保留 上方oneplace完整性
    one_place_data = deepcopy(one_place)
    _place = one_place_data.pop('place')
    _card = one_place_data.pop('card')
    # 優先搜尋place&card , 如有對應的則使用defaults update, 如無則 create !
    one_data, created = DiscountData.objects.update_or_create(place=_place, card=_card, defaults=one_place_data)
    return one_data, created

def create_info(oneplace_info, master_name, card, card_name, card_english_name, discount_type, discount_url):
    # # 分店為各一處位置
    # print("店名:", oneplace_info.get("place",""))
    # print("線上訂位:", oneplace_info.get("reserve_url",""))
    # print("address: ", oneplace_info.get("address",""))
    # print("place_web_url: ", oneplace_info.get("place_web_url",""))
    # print("phone: ", oneplace_info.get("phone",""))
    place = master_name + "-" + oneplace_info.get("place","")
    address = oneplace_info.get("address","")
    one_place={
        "place": place,
        "reserve_url": oneplace_info.get("reserve_url",""),
        "card": card,
        "card_name": card_name,
        "card_english_name": card_english_name,
        "discount_type": discount_type,
        "discount_url": discount_url ,
        "google_map_url":find_google_map_url( place, address),
        "place_web_url": oneplace_info.get("place_web_url",""),
        "phone": oneplace_info.get("phone",""),
        "address": address
        }
    return create_to_db(one_place)


@shared_task
def soup_store_info(s_string, master_name ,base_url, discount_type, discount_type_url, card, card_name, card_english_name):
    s = BeautifulSoup(s_string, "html.parser")
    all_place = []
    oneplace_info = {}
    # 單個優惠店家頁面
    discount_url = base_url + s.select_one('a').get('href','')
    discount_description = ','.join( [ i.text for i in s.select('p') ] )
    r_one_store = requests.get(discount_url)
    soup_page_one_store = BeautifulSoup(r_one_store.text, "html.parser")
    # print(discount_url)
    # print(master_name)
    detail_ = soup_page_one_store.select("div.pad-1-t.pad-1-b")[5].select("p")[0]
    detail_info = detail_.find_all("p")
    # detail_info = detail_.find_all("p", text=re.compile("|".join(detail_info_string_list)))
    for o in detail_info:
        text = o.text
        if o.get('style') != None:
            if oneplace_info != {}:
                one_data, created = create_info(oneplace_info, master_name, card, card_name, card_english_name, discount_type, discount_url)
                all_place.append(master_name + "-" + oneplace_info.get("place",""))
            break
        # 如果text為&nbsp; 則代表有別家分店
        if text  == u'\xa0':
            one_data, created = create_info(oneplace_info, master_name, card, card_name, card_english_name, discount_type, discount_url)
            all_place.append(master_name + "-" + oneplace_info.get("place",""))
            oneplace_info = {}
        else:
            if "：" in text:
                key = text.split("：")[0]
                value = text.split("：")[1]
                if "地　　址" in key :
                    oneplace_info.setdefault( "address", replace_space(value))
                elif "網　　址" in key :
                    oneplace_info.setdefault( "place_web_url", value)
                elif "電話預訂" in key :
                    oneplace_info.setdefault( "phone", replace_space(value))
                elif "電　　話" in key :
                    oneplace_info.setdefault( "phone", replace_space(value))
                elif "線上訂位":
                    oneplace_info.setdefault( "reserve_url", replace_space(value))
            else:
                oneplace_info.setdefault("place",text)
    return {"success":all_place}



@shared_task
def print_task(x):
    print(x)
    return {"success":x}