from django.contrib import admin
from .models import SiteSetting, CustomTextSnippet, Director, PageViewLog

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'tagline', 'established_year', 'phone', 'email')

    fieldsets = (
        ('General Site Branding & Hero Text', {
            'fields': ('site_name', 'hero_title', 'hero_subtext', 'tagline', 'established_year', 'address', 'phone', 'email')
        }),
        ('Action Buttons & Headers', {
            'fields': ('donate_button_text', 'anonymous_button_text', 'emergency_counseling_heading'),
        }),
        ('Donation & Bank Details', {
            'fields': ('mtn_mobile_money', 'airtel_money', 'bank_details'),
        }),
        ('About Us Content', {
            'fields': ('about_text', 'mission', 'vision'),
        }),
    )

@admin.register(CustomTextSnippet)
class CustomTextSnippetAdmin(admin.ModelAdmin):
    list_display = ('key', 'description', 'content')
    search_fields = ('key', 'description', 'content')

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'photo', 'order')
    list_editable = ('order',)
    fields = ('name', 'title', 'bio', 'photo', 'order')

@admin.register(PageViewLog)
class PageViewLogAdmin(admin.ModelAdmin):
    list_display = ('path', 'user', 'ip_address', 'timestamp')
    list_filter = ('path', 'timestamp')
    readonly_fields = ('path', 'user', 'ip_address', 'timestamp')
