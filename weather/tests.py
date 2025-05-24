from django.test import TestCase
from django.urls import reverse

class WeatherTests(TestCase):
    def test_homepage_loads(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_post_weather_search(self):
        response = self.client.post(reverse('index'), {'city': 'Tashkent'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Tashkent', str(response.content))
