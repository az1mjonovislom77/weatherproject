from django.urls import path
from .api_views import WeatherAPIView, UserSearchHistoryList, CityStatsList

urlpatterns = [
    path('weather/', WeatherAPIView.as_view(), name='weather'),
    path('history/', UserSearchHistoryList.as_view(), name='search-history'),
    path('stats/', CityStatsList.as_view(), name='city-stats'),
]
