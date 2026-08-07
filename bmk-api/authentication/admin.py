from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'school', 'is_staff')
    list_filter = ('role', 'school', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    autocomplete_fields = ('school',)
    fieldsets = UserAdmin.fieldsets + (
        ('School Administration Roles', {'fields': ('role', 'phone_number', 'school')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('School Administration Roles', {'fields': ('role', 'phone_number', 'school')}),
    )


admin.site.register(User, CustomUserAdmin)
