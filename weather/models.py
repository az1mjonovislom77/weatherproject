from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    city = models.CharField(max_length=100)
    searched_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class CityStats(models.Model):
    city = models.CharField(max_length=100, unique=True)
    search_count = models.IntegerField(default=0)
    objects = models.Manager()
