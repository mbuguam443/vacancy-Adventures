from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<slug:slug>/', views.book_tour, name='book_tour'),
    path('my/', views.user_bookings, name='user_bookings'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('review/<slug:slug>/', views.add_review, name='add_review'),
]
