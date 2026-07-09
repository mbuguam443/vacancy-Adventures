from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from tours.models import TourPackage, TourDate
from .models import Booking, Review
from payments.models import Payment
import uuid

@login_required
def book_tour(request, slug):
    tour = get_object_or_404(TourPackage, slug=slug, status='published')
    if request.method == 'POST':
        tour_date_id = request.POST.get('tour_date_id')
        adults = int(request.POST.get('adults', 1))
        children = int(request.POST.get('children', 0))
        special_requests = request.POST.get('special_requests', '')
        total_guests = adults + children

        if total_guests < 1:
            messages.error(request, 'At least 1 guest is required.')
            return redirect('tour_detail', slug=slug)

        tour_date = None
        if tour_date_id:
            tour_date = get_object_or_404(TourDate, id=tour_date_id, tour=tour, is_active=True)
            if tour_date.date < timezone.now().date():
                messages.error(request, 'Selected date has already passed.')
                return redirect('tour_detail', slug=slug)
            if total_guests > tour_date.available_seats:
                messages.error(request, f'Sorry, only {tour_date.available_seats} seats available on {tour_date.date.strftime("%d %b %Y")}.')
                return redirect('tour_detail', slug=slug)

        price_per_person = tour.discount_price if tour.discount_price else tour.price
        if tour_date and tour_date.price_adjustment:
            price_per_person += tour_date.price_adjustment
        total_price = price_per_person * total_guests

        booking = Booking.objects.create(
            user=request.user,
            tour=tour,
            tour_date=tour_date,
            travel_date=tour_date.date if tour_date else None,
            adults=adults,
            children=children,
            special_requests=special_requests,
            total_price=total_price,
        )

        Payment.objects.create(
            booking=booking,
            amount=total_price,
            method='mpesa',
            reference_number=f'MP-{uuid.uuid4().hex[:12].upper()}',
            status='pending',
        )

        messages.success(request, 'Booking created! Please complete payment.')
        return redirect('payments:mpesa_payment', booking_id=booking.id)

    return redirect('tour_detail', slug=slug)

@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'bookings/user_bookings.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'approved':
        if booking.tour_date:
            booking.tour_date.available_seats += booking.total_guests()
            booking.tour_date.save()
        tour = booking.tour
        tour.available_seats += booking.total_guests()
        tour.save()
        booking.status = 'cancelled'
        booking.save()
        if hasattr(booking, 'payment') and booking.payment.status == 'completed':
            booking.payment.status = 'refunded'
            booking.payment.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'Only approved bookings can be cancelled.')
    return redirect('bookings:user_bookings')

@login_required
def add_review(request, slug):
    tour = get_object_or_404(TourPackage, slug=slug)
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        booking_id = request.POST.get('booking_id')

        if not rating or not comment:
            messages.error(request, 'Please provide both rating and comment.')
            return redirect('tour_detail', slug=slug)

        booking = None
        if booking_id:
            booking = Booking.objects.filter(id=booking_id, user=request.user).first()

        review, created = Review.objects.update_or_create(
            user=request.user,
            tour=tour,
            defaults={
                'booking': booking,
                'rating': rating,
                'comment': comment,
                'is_active': True,
            }
        )
        if created:
            messages.success(request, 'Review submitted successfully!')
        else:
            messages.success(request, 'Review updated successfully!')
    return redirect('tour_detail', slug=slug)
