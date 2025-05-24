from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse

class WeatherTests(TestCase):
    def test_index_get(self):
        resp = self.client.get(reverse('weather:index'))
        self.assertEqual(resp.status_code, 200)

    def test_search_city(self):
        resp = self.client.post(reverse('weather:index'), {'city':'Tashkent'})
        self.assertContains(resp, 'Tashkent')

class StatsAPITest(APITestCase):
    def test_stats_endpoint(self):
        resp = self.client.get(reverse('weather_api:stats'))
        self.assertEqual(resp.status_code, 200)