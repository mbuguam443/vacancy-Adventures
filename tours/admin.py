from django.contrib import admin
from .models import Destination, Hotel, Vehicle, TourGuide, TourPackage, TourImage

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'status', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['status', 'country']
    search_fields = ['name', 'description']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_active']
    list_filter = ['is_active', 'rating']
    search_fields = ['name']

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['name', 'vehicle_type', 'capacity', 'is_active']
    list_filter = ['is_active', 'vehicle_type']

@admin.register(TourGuide)
class TourGuideAdmin(admin.ModelAdmin):
    list_display = ['name', 'experience_years', 'is_active']
    list_filter = ['is_active']

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ['title', 'destination', 'price', 'available_seats', 'status', 'is_featured']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['status', 'category', 'difficulty', 'is_featured']
    search_fields = ['title', 'description']
    inlines = [TourImageInline]

@admin.register(TourImage)
class TourImageAdmin(admin.ModelAdmin):
    list_display = ['tour', 'caption', 'is_main']
    list_filter = ['is_main']
