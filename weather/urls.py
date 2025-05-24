from django.urls import path
from .views import index, city_autocomplete

app_name = 'weather'

urlpatterns = [
    path("", index, name="index"),
    path('api/city-autocomplete/', city_autocomplete, name='city-autocomplete'),
]
