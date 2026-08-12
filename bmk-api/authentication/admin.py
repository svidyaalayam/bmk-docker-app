from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'school',
        'email_verified',
        'is_active',
        'is_staff',
    )
    list_filter = (
        'role',
        'school',
        'email_verified',
        'is_active',
        'is_staff',
        'is_superuser',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    autocomplete_fields = ('school',)
    fieldsets = UserAdmin.fieldsets + (
        (
            'School Administration Roles',
            {'fields': ('role', 'phone_number', 'school', 'email_verified', 'profile_locked', 'avatar')},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'School Administration Roles',
            {'fields': ('role', 'phone_number', 'school', 'email_verified', 'profile_locked', 'avatar')},
        ),
    )


admin.site.register(User, CustomUserAdmin)
