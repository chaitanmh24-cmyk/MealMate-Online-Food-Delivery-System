from django.contrib import admin
from .models import SearchHistory

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'query', 'filters', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'query')
