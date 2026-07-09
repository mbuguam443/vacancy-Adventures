from django.urls import path
from . import views

urlpatterns = [
    path('destinations/', views.destination_list, name='destination_list'),
    path('destination/<slug:slug>/', views.destination_detail, name='destination_detail'),
    path('tours/', views.tour_list, name='tour_list'),
    path('tour/<slug:slug>/', views.tour_detail, name='tour_detail'),
]
