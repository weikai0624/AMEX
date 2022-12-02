import os
import sys
import json
import folium
from urllib.parse import urlparse, parse_qsl, quote
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from map.models import DiscountData

def find_google_map_url(place, address):
    base_google_search_url = "https://www.google.com/maps/place?q="
    place_quote =  quote(place.encode('utf8'))
    address_quote = address
    query_quote = place_quote + " " +address_quote
    return base_google_search_url+query_quote

def create_folium_map(request):
    card = int( request.GET.get('card',3) )
    data = DiscountData.objects.filter(card=card)
    discount_type_set = set([i.discount_type for i in data])

    feature_group_map = { i: folium.FeatureGroup(name=i) for i in discount_type_set }
    icon_group_map = {
        "美食饗味":{
                'color':'red',
                'icon': 'heart'
            },
        "買一晚送一晚":{
                'color':'lightgreen',
                'icon': 'hotel'
            },
        "住一晚優惠價":{
                'color':'green',
                'icon': 'hotel'
            },
        "購物生活":{
                'color':'blue',
                'icon': 'shopping-cart'
            },
    }
    folium_map = folium.Map(location=[25.04337438, 121.52811992],attr='AMEXdata',zoom_start=12)
    
    for one in data:
        if one.latitude == 0 or one.longitude == 0:
            continue
        place = one.place
        card_name = one.card_name
        address = one.address
        discount_type = one.discount_type
        discount_url = one.discount_url

        # 預設為地址搜尋, 如果有詳細店家 google map 地圖請手動更新
        if one.google_map_url == '' or one.google_map_url == None:
            google_map = find_google_map_url(place, address)
        else:
            google_map = one.google_map_url

        icon_style=icon_group_map[discount_type]
        iframe = folium.IFrame(f'\
            <p>店家: {place}<p/>\
            <p>地址: {address}<p/>\
            <p>卡別: {card_name}<p/>\
            <p>優惠方案: {discount_type}<p/>\
            <p>優惠頁面: <a href="{discount_url}" target="_blank"> 點擊連結運通卡頁面連結 </a><p/>\
            <p>地圖搜尋:<a href="{google_map}" target="_blank"> 點擊連結至Google 地圖 </a><p/>\
            <p><p/>\
            <p>實際優惠及詳情請依美國運通卡官方為主<p/>\
            ')
        popup = folium.Popup(iframe, min_width=300, max_width=300)

        if one.longitude == None: one.longitude = 0
        if one.latitude == None: one.latitude = 0
    
        folium.Marker(
            location=[one.latitude, one.longitude],
            popup=popup,
            tooltip=place,
            icon=folium.Icon(color=icon_style['color'], icon=icon_style['icon'], prefix='fa'),
            ).add_to(feature_group_map[discount_type])
    
    for j in feature_group_map.values():
        j.add_to(folium_map)
    folium.LayerControl(title="CREATE").add_to(folium_map)

    folium_map.save("index.html")

    return HttpResponse(folium_map._repr_html_())


if __name__ == "__main__":
    create_folium_map('')