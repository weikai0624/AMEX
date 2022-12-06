from urllib.parse import quote
from copy import deepcopy

def replace_space(string):
    return string.replace(" ","").replace("\r", "").replace("\n", "")

def find_google_map_url(place, address):
    base_google_search_url = "https://www.google.com/maps/place?q="
    place_quote =  quote(place.encode('utf8'))
    address_quote = address
    query_quote = place_quote + " " +address_quote
    return base_google_search_url+query_quote
