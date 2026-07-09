from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('mpesa/<int:booking_id>/', views.mpesa_payment_page, name='mpesa_payment'),
    path('mpesa/<int:booking_id>/initiate/', views.initiate_stk_push, name='initiate_stk_push'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
]
