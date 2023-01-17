from django.db import models
from datetime import datetime

# Create your models here.

class DiscountData(models.Model):
    card = models.IntegerField(null=True)
    card_english_name = models.CharField(max_length=99999,null=True)
    card_name = models.CharField(max_length=99999,null=True)
    place = models.CharField(max_length=99999)
    discount_type = models.CharField(max_length=99999,null=True)
    discount_description = models.CharField(max_length=99999,null=True)
    discount_url = models.URLField()
    place_web_url = models.URLField(null=True, blank=True)
    reserve_url = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=99999,null=True, blank=True)
    address = models.CharField(max_length=99999,null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    google_map_url = models.CharField(max_length=99999, null=True, blank=True)
    udpate_datetime = models.DateTimeField(auto_now=True)
    