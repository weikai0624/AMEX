
from django.urls import path
from map import views
from map import show_folium_map
from rest_framework.routers import DefaultRouter
from map.data_view import DiscountDataAPI


urlpatterns = [
    path('show/', show_folium_map.create_folium_map, name='show_map'),
    path('create/', views.create_data, name='create_data'),
    path('create/coordinate/', views.create_coordinate_data, name='create_coordinate_data'),
    path('create/coordinate/google/api/', views.create_coordinate_data_google_api, name='create_coordinate_data_google_api')
]

router = DefaultRouter()
router.register(r'data', DiscountDataAPI, basename='discount_data')

urlpatterns += router.urls