from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'role', 'phone', 'specialty', 'is_active', 'is_staff')
    list_display_links = ('username', 'get_full_name')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('role', 'last_name')
    list_editable = ('role', 'is_active')

    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'password'),
        }),
        ('Personal Information', {
            'fields': (('first_name', 'last_name'), 'email', 'phone', 'profile_picture'),
        }),
        ('Professional Details', {
            'fields': ('role', 'specialty'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        ('Login Credentials', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal Information', {
            'fields': (('first_name', 'last_name'), 'email', 'phone'),
        }),
        ('Professional Details', {
            'fields': ('role', 'specialty'),
        }),
        ('Status', {
            'fields': ('is_active', 'is_staff'),
        }),
    )

    readonly_fields = ('created_at', 'last_login', 'date_joined')
