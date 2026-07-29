from django.contrib import admin
from .models import CounselingSession, AnonymousSupportThread, AnonymousMessage

class AnonymousMessageInline(admin.TabularInline):
    model = AnonymousMessage
    extra = 1

@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    list_display = ('client', 'counselor', 'session_type', 'preferred_date', 'status')
    list_filter = ('status', 'session_type', 'preferred_date')
    search_fields = ('client__username', 'notes')

@admin.register(AnonymousSupportThread)
class AnonymousSupportThreadAdmin(admin.ModelAdmin):
    list_display = ('token', 'category', 'is_active', 'created_at')
    inlines = [AnonymousMessageInline]
