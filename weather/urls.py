from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.index, name='index'),
    path('autocomplete/', views.city_autocomplete, name='city-autocomplete'),
    path('stats/', views.search_stats_api, name='search-stats-api'),
]
