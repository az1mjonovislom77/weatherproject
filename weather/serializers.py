from rest_framework import serializers
from .models import SearchHistory, CityStats

class SearchHistorySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField() 

    class Meta:
        model = SearchHistory
        fields = ['id', 'user', 'city', 'searched_at']

class CityStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityStats
        fields = ['city', 'search_count']
