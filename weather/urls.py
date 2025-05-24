from django.urls import path
from .views import WeatherView, CityAutocompleteView, SearchStatsAPIView

app_name = "weather"

urlpatterns = [
    path('', WeatherView.as_view(), name='index'),
    path('autocomplete/', CityAutocompleteView.as_view(), name='autocomplete'),
    path('stats/', SearchStatsAPIView.as_view(), name='stats'),
]
