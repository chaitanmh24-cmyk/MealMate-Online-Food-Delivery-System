from django.contrib import admin
from .models import Category, FoodItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'icon', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'restaurant', 'category', 'cuisine', 'food_type', 'price', 'is_available')
    list_filter = ('food_type', 'is_available', 'category', 'cuisine', 'restaurant')
    search_fields = ('name', 'description', 'restaurant__name')
    list_editable = ('price', 'is_available')
