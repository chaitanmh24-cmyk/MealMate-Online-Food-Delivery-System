from django.contrib import admin
from .models import Cuisine, Restaurant

@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'restaurant_type', 'city', 'rating', 'is_active')
    list_filter = ('restaurant_type', 'city', 'is_active')
    search_fields = ('name', 'address', 'city')
    filter_horizontal = ('cuisines',)
