from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'mobile_number', 'gender', 'city', 'is_staff', 'is_active')
    list_filter = ('gender', 'is_staff', 'is_superuser', 'is_active', 'city')
    search_fields = ('username', 'email', 'mobile_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('mobile_number', 'gender', 'address', 'city')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'mobile_number', 'gender', 'address', 'city')}),
    )
