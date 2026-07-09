from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.customer_dashboard, name='customer_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),

    # Tours
    path('admin/tours/', views.TourPackageList.as_view(), name='admin_tour_list'),
    path('admin/tours/create/', views.get_tour_form, name='admin_tour_create'),
    path('admin/tours/<int:pk>/edit/', views.get_tour_form, name='admin_tour_edit'),
    path('admin/tours/<int:pk>/delete/', views.delete_tour, name='admin_tour_delete'),

    # Destinations
    path('admin/destinations/', views.DestinationList.as_view(), name='admin_destination_list'),
    path('admin/destinations/create/', views.get_destination_form, name='admin_destination_create'),
    path('admin/destinations/<int:pk>/edit/', views.get_destination_form, name='admin_destination_edit'),
    path('admin/destinations/<int:pk>/delete/', views.delete_destination, name='admin_destination_delete'),

    # Hotels
    path('admin/hotels/', views.HotelList.as_view(), name='admin_hotel_list'),
    path('admin/hotels/create/', views.get_hotel_form, name='admin_hotel_create'),
    path('admin/hotels/<int:pk>/edit/', views.get_hotel_form, name='admin_hotel_edit'),
    path('admin/hotels/<int:pk>/delete/', views.delete_hotel, name='admin_hotel_delete'),

    # Vehicles
    path('admin/vehicles/', views.VehicleList.as_view(), name='admin_vehicle_list'),
    path('admin/vehicles/create/', views.get_vehicle_form, name='admin_vehicle_create'),
    path('admin/vehicles/<int:pk>/edit/', views.get_vehicle_form, name='admin_vehicle_edit'),
    path('admin/vehicles/<int:pk>/delete/', views.delete_vehicle, name='admin_vehicle_delete'),

    # Tour Guides
    path('admin/guides/', views.GuideList.as_view(), name='admin_guide_list'),
    path('admin/guides/create/', views.get_guide_form, name='admin_guide_create'),
    path('admin/guides/<int:pk>/edit/', views.get_guide_form, name='admin_guide_edit'),
    path('admin/guides/<int:pk>/delete/', views.delete_guide, name='admin_guide_delete'),

    # Tour Dates
    path('admin/tour-dates/', views.TourDateList.as_view(), name='admin_tourdate_list'),
    path('admin/tour-dates/create/', views.get_tourdate_form, name='admin_tourdate_create'),
    path('admin/tour-dates/<int:pk>/edit/', views.get_tourdate_form, name='admin_tourdate_edit'),
    path('admin/tour-dates/<int:pk>/delete/', views.delete_tourdate, name='admin_tourdate_delete'),

    # Bookings
    path('admin/bookings/', views.BookingList.as_view(), name='admin_booking_list'),
    path('admin/bookings/<int:pk>/edit/', views.get_booking_form, name='admin_booking_edit'),
    path('admin/bookings/<int:pk>/delete/', views.delete_booking, name='admin_booking_delete'),

    # Reviews
    path('admin/reviews/', views.ReviewList.as_view(), name='admin_review_list'),
    path('admin/reviews/<int:pk>/edit/', views.get_review_form, name='admin_review_edit'),
    path('admin/reviews/<int:pk>/delete/', views.delete_review, name='admin_review_delete'),

    # Payments
    path('admin/payments/', views.PaymentList.as_view(), name='admin_payment_list'),
    path('admin/payments/<int:pk>/delete/', views.delete_payment, name='admin_payment_delete'),

    # Blog Posts
    path('admin/blog-posts/', views.BlogPostList.as_view(), name='admin_blogpost_list'),
    path('admin/blog-posts/create/', views.get_blogpost_form, name='admin_blogpost_create'),
    path('admin/blog-posts/<int:pk>/edit/', views.get_blogpost_form, name='admin_blogpost_edit'),
    path('admin/blog-posts/<int:pk>/delete/', views.delete_blogpost, name='admin_blogpost_delete'),

    # Blog Categories
    path('admin/blog-categories/', views.BlogCategoryList.as_view(), name='admin_blogcategory_list'),
    path('admin/blog-categories/create/', views.get_blogcategory_form, name='admin_blogcategory_create'),
    path('admin/blog-categories/<int:pk>/edit/', views.get_blogcategory_form, name='admin_blogcategory_edit'),
    path('admin/blog-categories/<int:pk>/delete/', views.delete_blogcategory, name='admin_blogcategory_delete'),

    # Services
    path('admin/services/', views.ServiceList.as_view(), name='admin_service_list'),
    path('admin/services/create/', views.get_service_form, name='admin_service_create'),
    path('admin/services/<int:pk>/edit/', views.get_service_form, name='admin_service_edit'),
    path('admin/services/<int:pk>/delete/', views.delete_service, name='admin_service_delete'),

    # Why Choose Us
    path('admin/why-choose-us/', views.WhyChooseUsList.as_view(), name='admin_whychooseus_list'),
    path('admin/why-choose-us/create/', views.get_whychooseus_form, name='admin_whychooseus_create'),
    path('admin/why-choose-us/<int:pk>/edit/', views.get_whychooseus_form, name='admin_whychooseus_edit'),
    path('admin/why-choose-us/<int:pk>/delete/', views.delete_whychooseus, name='admin_whychooseus_delete'),

    # Testimonials
    path('admin/testimonials/', views.TestimonialList.as_view(), name='admin_testimonial_list'),
    path('admin/testimonials/create/', views.get_testimonial_form, name='admin_testimonial_create'),
    path('admin/testimonials/<int:pk>/edit/', views.get_testimonial_form, name='admin_testimonial_edit'),
    path('admin/testimonials/<int:pk>/delete/', views.delete_testimonial, name='admin_testimonial_delete'),

    # Gallery
    path('admin/gallery/', views.GalleryList.as_view(), name='admin_gallery_list'),
    path('admin/gallery/create/', views.get_gallery_form, name='admin_gallery_create'),
    path('admin/gallery/<int:pk>/edit/', views.get_gallery_form, name='admin_gallery_edit'),
    path('admin/gallery/<int:pk>/delete/', views.delete_gallery, name='admin_gallery_delete'),

    # FAQs
    path('admin/faqs/', views.FAQList.as_view(), name='admin_faq_list'),
    path('admin/faqs/create/', views.get_faq_form, name='admin_faq_create'),
    path('admin/faqs/<int:pk>/edit/', views.get_faq_form, name='admin_faq_edit'),
    path('admin/faqs/<int:pk>/delete/', views.delete_faq, name='admin_faq_delete'),

    # Contact Messages
    path('admin/messages/', views.MessageList.as_view(), name='admin_message_list'),
    path('admin/messages/<int:pk>/', views.message_detail, name='admin_message_detail'),
    path('admin/messages/<int:pk>/delete/', views.delete_message, name='admin_message_delete'),

    # Subscribers
    path('admin/subscribers/', views.SubscriberList.as_view(), name='admin_subscriber_list'),
    path('admin/subscribers/<int:pk>/delete/', views.delete_subscriber, name='admin_subscriber_delete'),

    # Customers
    path('admin/customers/', views.CustomerList.as_view(), name='admin_customer_list'),
    path('admin/customers/<int:pk>/edit/', views.get_customer_form, name='admin_customer_edit'),
    path('admin/customers/<int:pk>/delete/', views.delete_customer, name='admin_customer_delete'),

    # Site Settings
    path('admin/site-settings/', views.SiteSettingList.as_view(), name='admin_sitesetting_list'),
    path('admin/site-settings/<int:pk>/edit/', views.get_sitesetting_form, name='admin_sitesetting_edit'),
    path('admin/site-settings/<int:pk>/delete/', views.delete_sitesetting, name='admin_sitesetting_delete'),
]
