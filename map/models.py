from django.db import models
from datetime import datetime

# Create your models here.

class DiscountData(models.Model):
    place = models.CharField(max_length=99999)
    discount_type = models.CharField(max_length=99999,null=True)
    discount_url = models.URLField()
    place_web_url = models.URLField(null=True)
    phone = models.CharField(max_length=99999,null=True)
    address = models.CharField(max_length=99999,null=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    google_map_url = models.CharField(max_length=99999,null=True)
    udpate_datetime = models.DateTimeField(auto_now=True)
    