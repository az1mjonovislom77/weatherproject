import requests
from django.views import View
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
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


class CityAutocompleteView(View):
    def get(self, request):
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


class WeatherView(FormView):
    template_name = 'weather/index.html'
    form_class = CityForm
    success_url = reverse_lazy("weather:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_city = self.request.COOKIES.get("last_city")
        if self.request.GET.get("last"):
            last_city = self.request.GET["last"]
        weather_data = None
        error = None
        searched_city = None

        if last_city and self.request.method == "GET":
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

        history = None
        if self.request.user.is_authenticated:
            history = SearchHistory.objects.filter(user=self.request.user).order_by('-searched_at')[:5]

        context.update({
            "weather": weather_data,
            "error": error,
            "searched_city": searched_city,
            "history": history,
            "last_city": last_city,
        })
        return context

    def form_valid(self, form):
        city = form.cleaned_data['city']
        lat, lon = get_coordinates(city)
        weather_data = None
        error = None
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

        if self.request.user.is_authenticated:
            SearchHistory.objects.create(user=self.request.user, city=city)
        cs, _ = CityStats.objects.get_or_create(city=city)
        cs.search_count += 1
        cs.save()

        context = self.get_context_data(form=form)
        context.update({
            "weather": weather_data,
            "searched_city": city,
            "error": error,
        })

        response = render(self.request, self.template_name, context)
        response.set_cookie("last_city", city, max_age=7 * 24 * 3600)
        return response


class SearchStatsAPIView(View):
    def get(self, request):
        stats = CityStats.objects.values('city', 'search_count').order_by('-search_count')
        return JsonResponse(list(stats), safe=False)
