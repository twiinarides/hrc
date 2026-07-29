from django.contrib import admin
from .models import Program, ProgramApplication


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active',)
    search_fields = ('title', 'summary', 'description')


@admin.register(ProgramApplication)
class ProgramApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'program', 'applicant', 'phone_number', 'status', 'submitted_at')
    list_filter = ('status', 'program', 'submitted_at')
    list_editable = ('status',)
    search_fields = ('full_name', 'phone_number', 'reason', 'applicant__username')
    readonly_fields = ('submitted_at', 'updated_at', 'applicant', 'program')
    date_hierarchy = 'submitted_at'
    fieldsets = (
        ('Applicant Info', {
            'fields': ('applicant', 'program', 'full_name', 'phone_number', 'age', 'submitted_at', 'updated_at')
        }),
        ('Application Details', {
            'fields': ('reason', 'additional_info')
        }),
        ('Admin Management', {
            'fields': ('status', 'admin_notes'),
            'classes': ('wide',)
        }),
    )
