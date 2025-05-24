import requests
from django.shortcuts import render
from django.http import JsonResponse
from .forms import CityForm
from .models import SearchHistory, CityStats

def get_coordinates(city):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    try:
        resp = requests.get(geo_url)
        results = resp.json().get('results', [])
        if results:
            return results[0]['latitude'], results[0]['longitude']
    except Exception:
        pass
    return None, None

def get_weather_description(code):
    descriptions = {
        0: "Ясно", 1: "Малооблачно", 2: "Малооблачно", 3: "Малооблачно",
        45: "Туман", 48: "Туман", 51: "Морось", 53: "Морось", 55: "Морось",
        61: "Дождь", 63: "Дождь", 65: "Дождь", 71: "Снег", 73: "Снег", 75: "Снег",
        80: "Ливни", 81: "Ливни", 82: "Ливни", 95: "Гроза", 96: "Гроза", 99: "Гроза",
    }
    return descriptions.get(code, "Неизвестно")

def city_autocomplete(request):
    q = request.GET.get('query', '')
    if not q:
        return JsonResponse([], safe=False)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=5"
    try:
        results = requests.get(url).json().get('results', [])
        suggestions = [r['name'] for r in results]
    except Exception:
        suggestions = []
    return JsonResponse(suggestions, safe=False)

def index(request):
    form = CityForm(request.POST or None)
    weather_data = None
    error = None
    searched_city = None
    last_city = request.COOKIES.get("last_city")
    if request.method == "GET" and request.GET.get('last'):
        last_city = request.GET['last']

    if last_city and not request.POST:
        searched_city = last_city
        lat, lon = get_coordinates(last_city)
        if lat is not None:
            api = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&current_weather=true&"
                f"hourly=temperature_2m,weathercode,relativehumidity_2m,"
                f"pressure_msl,windspeed_10m,winddirection_10m,cloudcover,"
                f"precipitation,snowfall&timezone=auto"
            )
            data = requests.get(api).json()
            cw = data.get("current_weather", {})
            hr = data.get("hourly", {})
            cw.update({
                'humidity': hr.get("relativehumidity_2m", [None])[0],
                'pressure': hr.get("pressure_msl", [None])[0],
                'cloudcover': hr.get("cloudcover", [None])[0],
                'precipitation': hr.get("precipitation", [None])[0],
                'snowfall': hr.get("snowfall", [None])[0],
                'description': get_weather_description(cw.get('weathercode'))
            })
            weather_data = cw

    if request.method == "POST" and form.is_valid():
        city = form.cleaned_data['city']
        searched_city = city
        lat, lon = get_coordinates(city)
        if lat is None:
            error = "Город не найден"
        else:
            api = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&current_weather=true&"
                f"hourly=temperature_2m,weathercode,relativehumidity_2m,"
                f"pressure_msl,windspeed_10m,winddirection_10m,cloudcover,"
                f"precipitation,snowfall&timezone=auto"
            )
            try:
                data = requests.get(api).json()
                cw = data.get("current_weather", {})
                hr = data.get("hourly", {})
                cw.update({
                    'humidity': hr.get("relativehumidity_2m", [None])[0],
                    'pressure': hr.get("pressure_msl", [None])[0],
                    'cloudcover': hr.get("cloudcover", [None])[0],
                    'precipitation': hr.get("precipitation", [None])[0],
                    'snowfall': hr.get("snowfall", [None])[0],
                    'description': get_weather_description(cw.get('weathercode'))
                })
                weather_data = cw
            except Exception:
                error = "Ошибка подключения к API погоды"

        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, city=city)
        cs, _ = CityStats.objects.get_or_create(city=city)
        cs.search_count += 1
        cs.save()

    history = None
    if request.user.is_authenticated:
        history = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')[:5]

    resp = render(request, "weather/index.html", {
        "form": form,
        "weather": weather_data,
        "searched_city": searched_city,
        "history": history,
        "error": error,
        "last_city": last_city,
    })
    if searched_city:
        resp.set_cookie("last_city", searched_city, max_age=7*24*3600)
    return resp

def search_stats_api(request):
    stats = CityStats.objects.values('city', 'search_count').order_by('-search_count')
    return JsonResponse(list(stats), safe=False)
