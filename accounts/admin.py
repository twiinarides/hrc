from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('HRC Specific Roles & Verification', {'fields': ('role', 'phone_number', 'is_phone_verified', 'profile_picture', 'bio')}),
    )
    list_display = ('username', 'email', 'role', 'phone_number', 'is_phone_verified', 'is_staff')
    list_filter = ('role', 'is_phone_verified', 'is_staff', 'is_active')
