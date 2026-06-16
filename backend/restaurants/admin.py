from django.contrib import admin
from .models import Category, Restaurant, FoodItem, Review


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """
    Custom Admin for Restaurant:
    - Displays all fields including the new location, veg_nonveg
    - Image is entered as a URL (text field)
    - Only staff/admin users can access this
    """
    list_display = ('name', 'location', 'veg_nonveg', 'status', 'owner', 'created_at')
    list_filter = ('veg_nonveg', 'status')
    search_fields = ('name', 'location')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'image_preview')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'owner')
        }),
        ('Location & Type', {
            'fields': ('location', 'veg_nonveg', 'status')
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
            'description': '⚠️ Paste a direct image URL (e.g. https://images.unsplash.com/...)'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        """Show a live preview of the pasted image URL."""
        from django.utils.html import format_html
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:200px; border-radius:8px; margin-top:8px;" />',
                obj.image
            )
        return "No image provided."
    image_preview.short_description = 'Image Preview'

    def has_add_permission(self, request):
        """Only Admin users (staff) can add restaurants."""
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        """Only Admin users can edit restaurants."""
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        """Only Admin users can delete restaurants."""
        return request.user.is_staff


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'category', 'veg_nonveg', 'price', 'is_available')
    list_filter = ('veg_nonveg', 'is_available', 'category')
    search_fields = ('name', 'restaurant__name')
    ordering = ('restaurant', 'name')
    readonly_fields = ('image_preview',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'restaurant', 'category')
        }),
        ('Details', {
            'fields': ('veg_nonveg', 'cuisine_type', 'price', 'is_available')
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
            'description': '⚠️ Paste a direct image URL (e.g. https://images.unsplash.com/...)'
        }),
    )

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:200px; border-radius:8px; margin-top:8px;" />',
                obj.image
            )
        return "No image provided."
    image_preview.short_description = 'Image Preview'

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'food_item', 'restaurant', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'food_item__name', 'restaurant__name')
