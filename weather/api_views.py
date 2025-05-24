from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
import requests
from .models import SearchHistory, CityStats
from .serializers import SearchHistorySerializer, CityStatsSerializer

def get_coordinates(city):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    try:
        response = requests.get(geo_url)
        data = response.json()
        results = data.get('results')
        if results:
            lat = results[0]['latitude']
            lon = results[0]['longitude']
            return lat, lon
    except Exception:
        pass
    return None, None

def get_weather_description(code):
    descriptions = {
        0: "Ясно",
        1: "Малооблачно",
        2: "Малооблачно",
        3: "Малооблачно",
        45: "Туман",
        48: "Туман",
        51: "Морось",
        53: "Морось",
        55: "Морось",
        61: "Дождь",
        63: "Дождь",
        65: "Дождь",
        71: "Снег",
        73: "Снег",
        75: "Снег",
        80: "Ливни",
        81: "Ливни",
        82: "Ливни",
        95: "Гроза",
        96: "Гроза",
        99: "Гроза",
    }
    return descriptions.get(code, "Неизвестно")

class WeatherAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        city = request.data.get('city')
        if not city:
            return Response({"error": "City name is required"}, status=status.HTTP_400_BAD_REQUEST)

        lat, lon = get_coordinates(city)
        if lat is None or lon is None:
            return Response({"error": "City not found"}, status=status.HTTP_404_NOT_FOUND)

        api_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true&"
            f"hourly=temperature_2m,weathercode,relativehumidity_2m,"
            f"pressure_msl,windspeed_10m,winddirection_10m,cloudcover,"
            f"precipitation,snowfall&timezone=auto"
        )

        try:
            response = requests.get(api_url)
            data = response.json()
            current_weather = data.get("current_weather", {})
            hourly = data.get("hourly", {})
            current_weather['humidity'] = hourly.get("relativehumidity_2m", [None])[0]
            current_weather['pressure'] = hourly.get("pressure_msl", [None])[0]
            current_weather['cloudcover'] = hourly.get("cloudcover", [None])[0]
            current_weather['precipitation'] = hourly.get("precipitation", [None])[0]
            current_weather['snowfall'] = hourly.get("snowfall", [None])[0]
            current_weather['description'] = get_weather_description(current_weather.get('weathercode'))

        except Exception:
            return Response({"error": "Error connecting to weather API"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        user = request.user if request.user.is_authenticated else None
        if user:
            SearchHistory.objects.create(user=user, city=city)

        city_stat, created = CityStats.objects.get_or_create(city=city)
        city_stat.search_count += 1
        city_stat.save()

        return Response({
            "city": city,
            "weather": current_weather
        }, status=status.HTTP_200_OK)


class UserSearchHistoryList(generics.ListAPIView):
    serializer_class = SearchHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user).order_by('-searched_at')

class CityStatsList(generics.ListAPIView):
    queryset = CityStats.objects.all().order_by('-search_count')
    serializer_class = CityStatsSerializer
    permission_classes = [permissions.AllowAny]