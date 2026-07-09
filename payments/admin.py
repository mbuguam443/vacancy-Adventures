from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'method', 'reference_number', 'status', 'paid_date']
    list_filter = ['status', 'method']
    search_fields = ['reference_number', 'booking__tour__title']
