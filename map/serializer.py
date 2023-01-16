from rest_framework import serializers
from map.models import DiscountData

class DiscountDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountData
        fields = "__all__"