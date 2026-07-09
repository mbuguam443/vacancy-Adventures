from django.contrib import admin
from .models import Booking, Review

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'tour', 'travel_date', 'total_price', 'status', 'booking_date']
    list_filter = ['status']
    search_fields = ['user__username', 'tour__title']
    date_hierarchy = 'booking_date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'tour', 'rating', 'is_active', 'created_at']
    list_filter = ['rating', 'is_active']
    search_fields = ['user__username', 'tour__title']
