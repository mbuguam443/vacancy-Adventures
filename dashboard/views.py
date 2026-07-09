from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib.auth.models import User

from bookings.models import Booking, Review
from payments.models import Payment
from core.models import ContactMessage, NewsletterSubscriber, Service, WhyChooseUs, Testimonial, Gallery, FAQ, SiteSetting
from tours.models import TourPackage, Destination, Hotel, Vehicle, TourGuide, TourImage, TourDate
from blog.models import BlogPost, BlogCategory
from dashboard.forms import (
    TourPackageForm, DestinationForm, HotelForm, VehicleForm, TourGuideForm, TourDateForm,
    BookingForm, ReviewForm, BlogPostForm, BlogCategoryForm,
    ServiceForm, WhyChooseUsForm, TestimonialForm, GalleryForm, FAQForm,
    SiteSettingForm, CustomerForm,
)


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='/accounts/login/')(view_func)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    login_url = '/accounts/login/'


# ─── Dashboard ───

@login_required
def customer_dashboard(request):
    user = request.user
    bookings = Booking.objects.filter(user=user).order_by('-booking_date')[:10]
    booking_count = Booking.objects.filter(user=user).count()
    completed_bookings = Booking.objects.filter(user=user, status='completed').count()
    pending_bookings = Booking.objects.filter(user=user, status='pending').count()
    total_spent = Payment.objects.filter(booking__user=user, status='completed').aggregate(total=Sum('amount'))['total'] or 0
    context = {
        'bookings': bookings, 'booking_count': booking_count,
        'completed_bookings': completed_bookings, 'pending_bookings': pending_bookings,
        'total_spent': total_spent,
    }
    return render(request, 'dashboard/customer_dashboard.html', context)


@staff_required
def admin_dashboard(request):
    total_customers = User.objects.filter(is_staff=False).count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    total_tours = TourPackage.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    recent_bookings = Booking.objects.order_by('-booking_date')[:10]
    recent_messages = ContactMessage.objects.filter(is_read=False)[:5]
    recent_subscribers = NewsletterSubscriber.objects.filter(is_active=True)[:5]
    monthly_revenue = Payment.objects.filter(
        status='completed', paid_date__year=timezone.now().year,
        paid_date__month=timezone.now().month
    ).aggregate(total=Sum('amount'))['total'] or 0
    context = {
        'total_customers': total_customers, 'total_bookings': total_bookings,
        'pending_bookings': pending_bookings, 'total_tours': total_tours,
        'total_revenue': total_revenue, 'monthly_revenue': monthly_revenue,
        'recent_bookings': recent_bookings, 'recent_messages': recent_messages,
        'recent_subscribers': recent_subscribers,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


# ─── Generic Admin CRUD Views ───

class AdminListView(StaffRequiredMixin, ListView):
    paginate_by = 5
    model_name = ''
    page_title = ''
    add_url_name = ''
    edit_url_name = ''
    delete_url_name = ''
    search_fields = []
    template_name = 'dashboard/admin/admin_list.html'
    columns = []

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['objects'] = ctx.get('object_list', [])
        ctx['page_title'] = self.page_title or self.model._meta.verbose_name_plural.title()
        ctx['model_name'] = self.model_name or self.model._meta.verbose_name_plural.title()
        ctx['columns'] = self.get_columns()
        ctx['add_url'] = reverse_lazy(self.add_url_name) if self.add_url_name else None
        ctx['edit_url'] = self.edit_url_name
        ctx['delete_url'] = self.delete_url_name
        ctx['search_field'] = bool(self.search_fields)
        return ctx

    def get_columns(self):
        return self.columns

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q and self.search_fields:
            filters = Q()
            for f in self.search_fields:
                filters |= Q(**{f'{f}__icontains': q})
            qs = qs.filter(filters)
        return qs


class AdminCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'dashboard/admin/admin_form.html'
    page_title = ''
    list_url_name = ''
    success_message = 'Created successfully.'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.page_title or f'Add {self.model._meta.verbose_name}'
        ctx['list_url'] = reverse_lazy(self.list_url_name)
        return ctx

    def get_success_url(self):
        return reverse_lazy(self.list_url_name)


class AdminUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'dashboard/admin/admin_form.html'
    page_title = ''
    list_url_name = ''
    success_message = 'Updated successfully.'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = self.page_title or f'Edit {self.model._meta.verbose_name}'
        ctx['list_url'] = reverse_lazy(self.list_url_name)
        return ctx

    def get_success_url(self):
        return reverse_lazy(self.list_url_name)


class AdminDeleteView(StaffRequiredMixin, DeleteView):
    template_name = 'dashboard/admin/admin_confirm_delete.html'
    list_url_name = ''

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['list_url'] = reverse_lazy(self.list_url_name)
        return ctx

    def get_success_url(self):
        messages.success(self.request, 'Deleted successfully.')
        return reverse_lazy(self.list_url_name)


# ─── Column helpers ───

class Column:
    def __init__(self, header, field, template='dashboard/admin/cell_text.html'):
        self.header = header
        self.field = field
        self.template_name = template

    def __getitem__(self, key):
        return getattr(self, key)


# ─── TOUR PACKAGES ───

class TourPackageList(AdminListView):
    model = TourPackage
    page_title = 'Tour Packages'
    model_name = 'Tour Packages'
    add_url_name = 'dashboard:admin_tour_create'
    edit_url_name = 'dashboard:admin_tour_edit'
    delete_url_name = 'dashboard:admin_tour_delete'
    search_fields = ['title', 'destination__name', 'category']
    columns = [
        Column('Title', 'title'),
        Column('Destination', 'destination'),
        Column('Price', 'price', 'dashboard/admin/cell_price.html'),
        Column('Duration', 'duration_days', 'dashboard/admin/cell_duration.html'),
        Column('Category', 'category', 'dashboard/admin/cell_badge.html'),
        Column('Status', 'status', 'dashboard/admin/cell_status.html'),
    ]


def get_tour_form(request, pk=None):
    instance = get_object_or_404(TourPackage, pk=pk) if pk else None
    if request.method == 'POST':
        form = TourPackageForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            tour = form.save()
            messages.success(request, 'Tour saved successfully.')
            return redirect('dashboard:admin_tour_list')
    else:
        form = TourPackageForm(instance=instance)
    page_title = 'Edit Tour Package' if instance else 'Add Tour Package'
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': page_title,
        'list_url': reverse('dashboard:admin_tour_list'),
    })


def delete_tour(request, pk):
    obj = get_object_or_404(TourPackage, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted successfully.')
        return redirect('dashboard:admin_tour_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_tour_list'),
    })


# ─── DESTINATION ───

class DestinationList(AdminListView):
    model = Destination
    page_title = 'Destinations'
    model_name = 'Destinations'
    add_url_name = 'dashboard:admin_destination_create'
    edit_url_name = 'dashboard:admin_destination_edit'
    delete_url_name = 'dashboard:admin_destination_delete'
    search_fields = ['name', 'country', 'city']
    columns = [
        Column('Name', 'name'),
        Column('Country', 'country'),
        Column('Status', 'status', 'dashboard/admin/cell_status.html'),
    ]


def get_destination_form(request, pk=None):
    instance = get_object_or_404(Destination, pk=pk) if pk else None
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Destination saved.')
            return redirect('dashboard:admin_destination_list')
    else:
        form = DestinationForm(instance=instance)
    page_title = 'Edit Destination' if instance else 'Add Destination'
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': page_title,
        'list_url': reverse('dashboard:admin_destination_list'),
    })


def delete_destination(request, pk):
    obj = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_destination_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_destination_list'),
    })


# ─── HOTEL ───

class HotelList(AdminListView):
    model = Hotel
    page_title = 'Hotels'
    model_name = 'Hotels'
    add_url_name = 'dashboard:admin_hotel_create'
    edit_url_name = 'dashboard:admin_hotel_edit'
    delete_url_name = 'dashboard:admin_hotel_delete'
    search_fields = ['name', 'address']
    columns = [Column('Name', 'name'), Column('Rating', 'rating'), Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html')]


def get_hotel_form(request, pk=None):
    instance = get_object_or_404(Hotel, pk=pk) if pk else None
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel saved.')
            return redirect('dashboard:admin_hotel_list')
    else:
        form = HotelForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Hotel' if instance else 'Add Hotel',
        'list_url': reverse('dashboard:admin_hotel_list'),
    })


def delete_hotel(request, pk):
    obj = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_hotel_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_hotel_list'),
    })


# ─── VEHICLE ───

class VehicleList(AdminListView):
    model = Vehicle
    page_title = 'Vehicles'
    model_name = 'Vehicles'
    add_url_name = 'dashboard:admin_vehicle_create'
    edit_url_name = 'dashboard:admin_vehicle_edit'
    delete_url_name = 'dashboard:admin_vehicle_delete'
    search_fields = ['name', 'vehicle_type']
    columns = [Column('Name', 'name'), Column('Type', 'vehicle_type'), Column('Capacity', 'capacity'), Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html')]


def get_vehicle_form(request, pk=None):
    instance = get_object_or_404(Vehicle, pk=pk) if pk else None
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle saved.')
            return redirect('dashboard:admin_vehicle_list')
    else:
        form = VehicleForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Vehicle' if instance else 'Add Vehicle',
        'list_url': reverse('dashboard:admin_vehicle_list'),
    })


def delete_vehicle(request, pk):
    obj = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_vehicle_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_vehicle_list'),
    })


# ─── TOUR GUIDE ───

class GuideList(AdminListView):
    model = TourGuide
    page_title = 'Tour Guides'
    model_name = 'Tour Guides'
    add_url_name = 'dashboard:admin_guide_create'
    edit_url_name = 'dashboard:admin_guide_edit'
    delete_url_name = 'dashboard:admin_guide_delete'
    search_fields = ['name', 'email']
    columns = [Column('Name', 'name'), Column('Experience', 'experience_years', 'dashboard/admin/cell_years.html'), Column('Phone', 'phone'), Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html')]


def get_guide_form(request, pk=None):
    instance = get_object_or_404(TourGuide, pk=pk) if pk else None
    if request.method == 'POST':
        form = TourGuideForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Guide saved.')
            return redirect('dashboard:admin_guide_list')
    else:
        form = TourGuideForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Tour Guide' if instance else 'Add Tour Guide',
        'list_url': reverse('dashboard:admin_guide_list'),
    })


def delete_guide(request, pk):
    obj = get_object_or_404(TourGuide, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_guide_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_guide_list'),
    })


# ─── TOUR DATES ───

class TourDateList(AdminListView):
    model = TourDate
    page_title = 'Tour Dates'
    model_name = 'Tour Dates'
    add_url_name = 'dashboard:admin_tourdate_create'
    edit_url_name = 'dashboard:admin_tourdate_edit'
    delete_url_name = 'dashboard:admin_tourdate_delete'
    search_fields = ['tour__title']
    columns = [Column('Tour', 'tour'), Column('Date', 'date', 'dashboard/admin/cell_date.html'), Column('Seats', 'available_seats'), Column('Adjustment', 'price_adjustment', 'dashboard/admin/cell_price.html'), Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html')]


def get_tourdate_form(request, pk=None):
    instance = get_object_or_404(TourDate, pk=pk) if pk else None
    if request.method == 'POST':
        form = TourDateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour date saved.')
            return redirect('dashboard:admin_tourdate_list')
    else:
        form = TourDateForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Tour Date' if instance else 'Add Tour Date',
        'list_url': reverse('dashboard:admin_tourdate_list'),
    })


def delete_tourdate(request, pk):
    obj = get_object_or_404(TourDate, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_tourdate_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_tourdate_list'),
    })


# ─── BOOKING ───

class BookingList(AdminListView):
    model = Booking
    page_title = 'Bookings'
    model_name = 'Bookings'
    edit_url_name = 'dashboard:admin_booking_edit'
    delete_url_name = 'dashboard:admin_booking_delete'
    search_fields = ['user__username', 'tour__title', 'status']
    columns = [
        Column('User', 'user'),
        Column('Tour', 'tour'),
        Column('Guests', 'adults', 'dashboard/admin/cell_guests.html'),
        Column('Total', 'total_price', 'dashboard/admin/cell_price.html'),
        Column('Status', 'status', 'dashboard/admin/cell_status.html'),
        Column('Date', 'booking_date', 'dashboard/admin/cell_date.html'),
    ]


def get_booking_form(request, pk=None):
    instance = get_object_or_404(Booking, pk=pk) if pk else None
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated.')
            return redirect('dashboard:admin_booking_list')
    else:
        form = BookingForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Booking',
        'list_url': reverse('dashboard:admin_booking_list'),
    })


def delete_booking(request, pk):
    obj = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_booking_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_booking_list'),
    })


# ─── REVIEW ───

class ReviewList(AdminListView):
    model = Review
    page_title = 'Reviews'
    model_name = 'Reviews'
    edit_url_name = 'dashboard:admin_review_edit'
    delete_url_name = 'dashboard:admin_review_delete'
    search_fields = ['user__username', 'tour__title']
    columns = [
        Column('User', 'user'),
        Column('Tour', 'tour'),
        Column('Rating', 'rating', 'dashboard/admin/cell_rating.html'),
        Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html'),
    ]


def get_review_form(request, pk=None):
    instance = get_object_or_404(Review, pk=pk) if pk else None
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated.')
            return redirect('dashboard:admin_review_list')
    else:
        form = ReviewForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Review',
        'list_url': reverse('dashboard:admin_review_list'),
    })


def delete_review(request, pk):
    obj = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_review_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_review_list'),
    })


# ─── PAYMENT ───

class PaymentList(AdminListView):
    model = Payment
    page_title = 'Payments'
    model_name = 'Payments'
    delete_url_name = 'dashboard:admin_payment_delete'
    search_fields = ['reference_number', 'booking__user__username', 'status']
    columns = [
        Column('Reference', 'reference_number'),
        Column('Booking', 'booking', 'dashboard/admin/cell_booking_link.html'),
        Column('Amount', 'amount', 'dashboard/admin/cell_price.html'),
        Column('Method', 'method'),
        Column('Status', 'status', 'dashboard/admin/cell_status.html'),
        Column('Date', 'paid_date', 'dashboard/admin/cell_datetime.html'),
    ]


def delete_payment(request, pk):
    obj = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_payment_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_payment_list'),
    })


# ─── BLOG POSTS ───

class BlogPostList(AdminListView):
    model = BlogPost
    page_title = 'Blog Posts'
    model_name = 'Blog Posts'
    add_url_name = 'dashboard:admin_blogpost_create'
    edit_url_name = 'dashboard:admin_blogpost_edit'
    delete_url_name = 'dashboard:admin_blogpost_delete'
    search_fields = ['title', 'category__name']
    columns = [
        Column('Title', 'title'),
        Column('Category', 'category'),
        Column('Author', 'author'),
        Column('Status', 'status', 'dashboard/admin/cell_status.html'),
        Column('Created', 'created_at', 'dashboard/admin/cell_date.html'),
    ]


def get_blogpost_form(request, pk=None):
    instance = get_object_or_404(BlogPost, pk=pk) if pk else None
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post saved.')
            return redirect('dashboard:admin_blogpost_list')
    else:
        form = BlogPostForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Blog Post' if instance else 'Add Blog Post',
        'list_url': reverse('dashboard:admin_blogpost_list'),
    })


def delete_blogpost(request, pk):
    obj = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_blogpost_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_blogpost_list'),
    })


# ─── BLOG CATEGORY ───

class BlogCategoryList(AdminListView):
    model = BlogCategory
    page_title = 'Blog Categories'
    model_name = 'Blog Categories'
    add_url_name = 'dashboard:admin_blogcategory_create'
    edit_url_name = 'dashboard:admin_blogcategory_edit'
    delete_url_name = 'dashboard:admin_blogcategory_delete'
    search_fields = ['name']
    columns = [Column('Name', 'name')]


def get_blogcategory_form(request, pk=None):
    instance = get_object_or_404(BlogCategory, pk=pk) if pk else None
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category saved.')
            return redirect('dashboard:admin_blogcategory_list')
    else:
        form = BlogCategoryForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Category' if instance else 'Add Category',
        'list_url': reverse('dashboard:admin_blogcategory_list'),
    })


def delete_blogcategory(request, pk):
    obj = get_object_or_404(BlogCategory, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_blogcategory_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_blogcategory_list'),
    })


# ─── SERVICE ───

class ServiceList(AdminListView):
    model = Service
    page_title = 'Services'
    model_name = 'Services'
    add_url_name = 'dashboard:admin_service_create'
    edit_url_name = 'dashboard:admin_service_edit'
    delete_url_name = 'dashboard:admin_service_delete'
    search_fields = ['title']
    columns = [Column('Icon', 'icon'), Column('Title', 'title'), Column('Order', 'order')]


def get_service_form(request, pk=None):
    instance = get_object_or_404(Service, pk=pk) if pk else None
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service saved.')
            return redirect('dashboard:admin_service_list')
    else:
        form = ServiceForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Service' if instance else 'Add Service',
        'list_url': reverse('dashboard:admin_service_list'),
    })


def delete_service(request, pk):
    obj = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_service_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_service_list'),
    })


# ─── WHY CHOOSE US ───

class WhyChooseUsList(AdminListView):
    model = WhyChooseUs
    page_title = 'Why Choose Us'
    model_name = 'Why Choose Us'
    add_url_name = 'dashboard:admin_whychooseus_create'
    edit_url_name = 'dashboard:admin_whychooseus_edit'
    delete_url_name = 'dashboard:admin_whychooseus_delete'
    search_fields = ['title']
    columns = [Column('Icon', 'icon'), Column('Title', 'title'), Column('Order', 'order')]


def get_whychooseus_form(request, pk=None):
    instance = get_object_or_404(WhyChooseUs, pk=pk) if pk else None
    if request.method == 'POST':
        form = WhyChooseUsForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Saved.')
            return redirect('dashboard:admin_whychooseus_list')
    else:
        form = WhyChooseUsForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Item' if instance else 'Add Item',
        'list_url': reverse('dashboard:admin_whychooseus_list'),
    })


def delete_whychooseus(request, pk):
    obj = get_object_or_404(WhyChooseUs, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_whychooseus_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_whychooseus_list'),
    })


# ─── TESTIMONIAL ───

class TestimonialList(AdminListView):
    model = Testimonial
    page_title = 'Testimonials'
    model_name = 'Testimonials'
    add_url_name = 'dashboard:admin_testimonial_create'
    edit_url_name = 'dashboard:admin_testimonial_edit'
    delete_url_name = 'dashboard:admin_testimonial_delete'
    search_fields = ['name', 'designation']
    columns = [Column('Name', 'name'), Column('Designation', 'designation'), Column('Rating', 'rating'), Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html')]


def get_testimonial_form(request, pk=None):
    instance = get_object_or_404(Testimonial, pk=pk) if pk else None
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial saved.')
            return redirect('dashboard:admin_testimonial_list')
    else:
        form = TestimonialForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Testimonial' if instance else 'Add Testimonial',
        'list_url': reverse('dashboard:admin_testimonial_list'),
    })


def delete_testimonial(request, pk):
    obj = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_testimonial_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_testimonial_list'),
    })


# ─── GALLERY ───

class GalleryList(AdminListView):
    model = Gallery
    page_title = 'Gallery'
    model_name = 'Gallery Items'
    add_url_name = 'dashboard:admin_gallery_create'
    edit_url_name = 'dashboard:admin_gallery_edit'
    delete_url_name = 'dashboard:admin_gallery_delete'
    search_fields = ['caption', 'category']
    columns = [Column('Image', 'image', 'dashboard/admin/cell_image.html'), Column('Caption', 'caption'), Column('Category', 'category'), Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html')]


def get_gallery_form(request, pk=None):
    instance = get_object_or_404(Gallery, pk=pk) if pk else None
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gallery item saved.')
            return redirect('dashboard:admin_gallery_list')
    else:
        form = GalleryForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Gallery Item' if instance else 'Add Gallery Item',
        'list_url': reverse('dashboard:admin_gallery_list'),
    })


def delete_gallery(request, pk):
    obj = get_object_or_404(Gallery, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_gallery_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_gallery_list'),
    })


# ─── FAQ ───

class FAQList(AdminListView):
    model = FAQ
    page_title = 'FAQs'
    model_name = 'FAQs'
    add_url_name = 'dashboard:admin_faq_create'
    edit_url_name = 'dashboard:admin_faq_edit'
    delete_url_name = 'dashboard:admin_faq_delete'
    search_fields = ['question']
    columns = [Column('Question', 'question'), Column('Order', 'order'), Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html')]


def get_faq_form(request, pk=None):
    instance = get_object_or_404(FAQ, pk=pk) if pk else None
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ saved.')
            return redirect('dashboard:admin_faq_list')
    else:
        form = FAQForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit FAQ' if instance else 'Add FAQ',
        'list_url': reverse('dashboard:admin_faq_list'),
    })


def delete_faq(request, pk):
    obj = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_faq_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_faq_list'),
    })


# ─── CONTACT MESSAGE ───

class MessageList(AdminListView):
    model = ContactMessage
    page_title = 'Contact Messages'
    model_name = 'Messages'
    edit_url_name = 'dashboard:admin_message_detail'
    delete_url_name = 'dashboard:admin_message_delete'
    search_fields = ['name', 'email', 'subject']
    columns = [Column('Name', 'name'), Column('Email', 'email'), Column('Subject', 'subject'), Column('Read', 'is_read', 'dashboard/admin/cell_boolean.html'), Column('Date', 'created_at', 'dashboard/admin/cell_date.html')]


def message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        msg.is_read = True
        msg.save()
        messages.success(request, 'Marked as read.')
        return redirect('dashboard:admin_message_list')
    return render(request, 'dashboard/admin/message_detail.html', {
        'msg': msg, 'list_url': reverse('dashboard:admin_message_list'),
    })


def delete_message(request, pk):
    obj = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_message_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_message_list'),
    })


# ─── NEWSLETTER SUBSCRIBER ───

class SubscriberList(AdminListView):
    model = NewsletterSubscriber
    page_title = 'Subscribers'
    model_name = 'Subscribers'
    delete_url_name = 'dashboard:admin_subscriber_delete'
    search_fields = ['email']
    columns = [Column('Email', 'email'), Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html'), Column('Subscribed', 'subscribed_at', 'dashboard/admin/cell_date.html')]


def delete_subscriber(request, pk):
    obj = get_object_or_404(NewsletterSubscriber, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_subscriber_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_subscriber_list'),
    })


# ─── CUSTOMERS ───

class CustomerList(AdminListView):
    model = User
    page_title = 'Customers'
    model_name = 'Customers'
    edit_url_name = 'dashboard:admin_customer_edit'
    delete_url_name = 'dashboard:admin_customer_delete'
    search_fields = ['username', 'email', 'first_name', 'last_name']
    columns = [Column('Username', 'username'), Column('Name', 'get_full_name'), Column('Email', 'email'), Column('Staff', 'is_staff', 'dashboard/admin/cell_boolean.html'), Column('Active', 'is_active', 'dashboard/admin/cell_boolean.html')]

    def get_queryset(self):
        return User.objects.all().order_by('username')


def get_customer_form(request, pk=None):
    instance = get_object_or_404(User, pk=pk) if pk else None
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated.')
            return redirect('dashboard:admin_customer_list')
    else:
        form = CustomerForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Customer',
        'list_url': reverse('dashboard:admin_customer_list'),
    })


def delete_customer(request, pk):
    obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_customer_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_customer_list'),
    })


# ─── SITE SETTINGS ───

class SiteSettingList(AdminListView):
    model = SiteSetting
    page_title = 'Site Settings'
    model_name = 'Site Settings'
    edit_url_name = 'dashboard:admin_sitesetting_edit'
    delete_url_name = 'dashboard:admin_sitesetting_delete'
    search_fields = ['site_name']
    columns = [Column('Site Name', 'site_name'), Column('Email', 'email'), Column('Phone', 'phone')]

    def get_queryset(self):
        return SiteSetting.objects.all().order_by('site_name')


def get_sitesetting_form(request, pk=None):
    instance = get_object_or_404(SiteSetting, pk=pk) if pk else None
    if request.method == 'POST':
        form = SiteSettingForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved.')
            return redirect('dashboard:admin_sitesetting_list')
    else:
        form = SiteSettingForm(instance=instance)
    return render(request, 'dashboard/admin/admin_form.html', {
        'form': form, 'page_title': 'Edit Site Settings',
        'list_url': reverse('dashboard:admin_sitesetting_list'),
    })


def delete_sitesetting(request, pk):
    obj = get_object_or_404(SiteSetting, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Deleted.')
        return redirect('dashboard:admin_sitesetting_list')
    return render(request, 'dashboard/admin/admin_confirm_delete.html', {
        'object': obj, 'list_url': reverse('dashboard:admin_sitesetting_list'),
    })
