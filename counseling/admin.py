from django.contrib import admin
from .models import CounselingSession, AnonymousSupportThread, AnonymousMessage, AdminNotification


class AnonymousMessageInline(admin.TabularInline):
    model = AnonymousMessage
    extra = 1
    fields = ('sender_is_counselor', 'content', 'timestamp')
    readonly_fields = ('timestamp',)


@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    list_display = ('client', 'session_type', 'preferred_date', 'status', 'counselor', 'created_at')
    list_filter = ('status', 'session_type', 'created_at')
    list_editable = ('status',)
    search_fields = ('client__username', 'notes')
    date_hierarchy = 'created_at'


@admin.register(AnonymousSupportThread)
class AnonymousSupportThreadAdmin(admin.ModelAdmin):
    list_display = ('token', 'category', 'is_active', 'message_count', 'created_at')
    list_filter = ('is_active', 'category')
    search_fields = ('token', 'category')
    inlines = [AnonymousMessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    list_editable = ('is_read',)
    search_fields = ('title', 'message')
    date_hierarchy = 'created_at'
