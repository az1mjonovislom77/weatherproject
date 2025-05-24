from django.contrib import admin
from .models import SearchHistory, CityStats

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'searched_at')  
    list_filter = ('searched_at', 'city')          
    search_fields = ('city', 'user__username')     

@admin.register(CityStats)
class CityStatsAdmin(admin.ModelAdmin):
    list_display = ('city', 'search_count')
    search_fields = ('city',)
