"""AMEX URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from map import views
from map import show_folium_map

urlpatterns = [
    path('', RedirectView.as_view(url='/map/show/') ),
    path('admin/', admin.site.urls),
    path('map/show/', show_folium_map.create_folium_map, name='show_map'),
    path('map/create/', views.create_map, name='create_map')
]
