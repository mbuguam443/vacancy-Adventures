import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from bookings.models import Booking
from .models import Payment

logger = logging.getLogger(__name__)


@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, booking__user=request.user)
    return render(request, 'payments/payment_detail.html', {'payment': payment})


@login_required
def mpesa_payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = getattr(booking, 'payment', None)
    if not payment:
        messages.error(request, 'No payment record found for this booking.')
        return redirect('bookings:booking_detail', booking_id=booking.id)
    if payment.status == 'completed':
        messages.info(request, 'This booking is already paid.')
        return redirect('bookings:booking_detail', booking_id=booking.id)
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        request.session['mpesa_phone'] = phone
        request.session['mpesa_booking_id'] = booking_id
        return redirect('payments:initiate_stk_push', booking_id=booking.id)
    return render(request, 'payments/mpesa_payment.html', {
        'booking': booking,
        'payment': payment,
    })


@login_required
def initiate_stk_push(request, booking_id):
    if request.method != 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'POST required'}, status=405)
        return redirect('payments:mpesa_payment', booking_id=booking_id)

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = getattr(booking, 'payment', None)
    if not payment or payment.status != 'pending':
        return redirect('bookings:booking_detail', booking_id=booking.id)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    phone = request.POST.get('phone', '').strip()
    if not phone:
        phone = request.session.pop('mpesa_phone', '')
    phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    if not phone.startswith('254'):
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        else:
            phone = '254' + phone

    if len(phone) != 12 or not phone.startswith('2547'):
        if is_ajax:
            return JsonResponse({'error': 'Enter a valid Safaricom number (0712345678)'}, status=400)
        messages.error(request, 'Enter a valid Safaricom number (e.g. 0712345678)')
        return redirect('payments:mpesa_payment', booking_id=booking.id)

    payment.phone_number = phone
    payment.save()

    if settings.MPESA_DEMO_MODE:
        payment.status = 'completed'
        payment.paid_date = timezone.now()
        payment.save()
        booking.status = 'approved'
        booking.save()
        booking.tour.available_seats -= booking.total_guests()
        booking.tour.save()
        if is_ajax:
            return JsonResponse({
                'success': True,
                'demo': True,
                'message': 'Demo payment completed!',
                'redirect': booking.get_absolute_url(),
            })
        messages.success(request, 'Payment completed successfully!')
        return redirect('bookings:booking_detail', booking_id=booking.id)

    try:
        from .mpesa import stk_push

        callback_url = settings.MPESA_CALLBACK_URL
        response = stk_push(
            phone=phone,
            amount=int(payment.amount),
            account_ref=f'Booking#{booking.id}',
            callback_url=callback_url,
        )

        if response.get('ResponseCode') == '0':
            payment.mpesa_checkout_id = response.get('CheckoutRequestID')
            payment.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'checkout_id': response['CheckoutRequestID'],
                    'message': 'STK Push sent. Check your phone.',
                })
            messages.success(request, 'STK Push sent! Check your phone to complete payment.')
            return redirect('bookings:booking_detail', booking_id=booking.id)
        else:
            payment.status = 'failed'
            payment.save()
            msg = f'M-Pesa error: {response.get("ResponseDescription", "Unknown")}'
            if is_ajax:
                return JsonResponse({'error': msg}, status=400)
            messages.error(request, msg)
            return redirect('payments:mpesa_payment', booking_id=booking.id)

    except Exception as e:
        logger.exception('STK push failed')
        if is_ajax:
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f'Payment failed: {e}')
        return redirect('payments:mpesa_payment', booking_id=booking.id)


@csrf_exempt
def mpesa_callback(request):
    if request.method != 'POST':
        return HttpResponse('OK')

    try:
        data = json.loads(request.body)
        stk = data.get('Body', {}).get('stkCallback', {})
        checkout_id = stk.get('CheckoutRequestID')
        result_code = stk.get('ResultCode')

        payment = Payment.objects.filter(mpesa_checkout_id=checkout_id).first()
        if not payment:
            logger.warning(f'Callback for unknown CheckoutRequestID: {checkout_id}')
            return HttpResponse('OK')

        if result_code == 0:
            items = stk.get('CallbackMetadata', {}).get('Item', [])
            mpesa_receipt = ''
            for item in items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    mpesa_receipt = item.get('Value', '')
                    break

            payment.status = 'completed'
            payment.paid_date = timezone.now()
            payment.mpesa_receipt = mpesa_receipt
            payment.save()

            booking = payment.booking
            booking.status = 'approved'
            booking.save()
            booking.tour.available_seats -= booking.total_guests()
            booking.tour.save()
        else:
            payment.status = 'failed'
            payment.save()

    except Exception as e:
        logger.exception('M-Pesa callback processing failed')

    return HttpResponse('OK')
