from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor_name', 'amount', 'currency', 'payment_method', 'transaction_reference', 'is_verified', 'created_at')
    list_filter = ('payment_method', 'is_verified', 'created_at')
    search_fields = ('donor_name', 'phone', 'transaction_reference')
    list_editable = ('is_verified',)
