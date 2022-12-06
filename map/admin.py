from django.contrib import admin
from map.models import DiscountData


class DiscountDataAdmin(admin.ModelAdmin):
    list_display = ('place', 'card_name','card', 'discount_type', 'address', 'google_map_url', 'udpate_datetime', 'longitude', 'latitude')
    list_filter = ('card', 'card_name', 'place', 'udpate_datetime')

admin.site.register(DiscountData, DiscountDataAdmin)