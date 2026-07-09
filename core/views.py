from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from tours.models import TourPackage, Destination
from blog.models import BlogPost
from .models import Service, WhyChooseUs, Testimonial, Gallery, FAQ, ContactMessage, NewsletterSubscriber

def home_view(request):
    featured_tours = TourPackage.objects.filter(status='published', is_featured=True)[:6]
    services = Service.objects.all()[:4]
    why_choose_us = WhyChooseUs.objects.all()[:4]
    testimonials = Testimonial.objects.filter(is_active=True)[:10]
    gallery_items = Gallery.objects.filter(is_active=True)[:12]
    blog_posts = BlogPost.objects.filter(status='published')[:3]
    destinations = Destination.objects.filter(status='published')[:6]
    context = {
        'featured_tours': featured_tours,
        'services': services,
        'why_choose_us': why_choose_us,
        'testimonials': testimonials,
        'gallery_items': gallery_items,
        'blog_posts': blog_posts,
        'destinations': destinations,
    }
    return render(request, 'core/home.html', context)

def about_view(request):
    services = Service.objects.all()[:4]
    why_choose_us = WhyChooseUs.objects.all()[:4]
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    context = {
        'services': services,
        'why_choose_us': why_choose_us,
        'testimonials': testimonials,
    }
    return render(request, 'core/about.html', context)

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message')
        if name and email and message:
            ContactMessage.objects.create(
                name=name, email=email, phone=phone,
                subject=subject, message=message
            )
            messages.success(request, 'Thank you! Your message has been sent successfully.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all required fields.')
    return render(request, 'core/contact.html')

def gallery_view(request):
    category = request.GET.get('category')
    gallery_items = Gallery.objects.filter(is_active=True)
    if category:
        gallery_items = gallery_items.filter(category=category)
    gallery_items = gallery_items.order_by('-created_at')
    paginator = Paginator(gallery_items, 12)
    page = request.GET.get('page', 1)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    categories = Gallery.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    return render(request, 'core/gallery.html', {
        'gallery_items': items,
        'categories': categories,
        'current_category': category,
    })

def faq_view(request):
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, 'core/faq.html', {'faqs': faqs})

def search_view(request):
    query = request.GET.get('q', '')
    destination_slug = request.GET.get('destination', '')
    duration = request.GET.get('duration', '')

    tours = TourPackage.objects.filter(status='published')
    destinations = Destination.objects.filter(status='published')

    if query:
        tours = tours.filter(
            Q(title__icontains=query) | Q(description__icontains=query) |
            Q(destination__name__icontains=query)
        )
    if destination_slug:
        tours = tours.filter(destination__slug=destination_slug)
    if duration:
        if duration == '1-3':
            tours = tours.filter(duration_days__gte=1, duration_days__lte=3)
        elif duration == '4-7':
            tours = tours.filter(duration_days__gte=4, duration_days__lte=7)
        elif duration == '8-14':
            tours = tours.filter(duration_days__gte=8, duration_days__lte=14)
        elif duration == '15+':
            tours = tours.filter(duration_days__gte=15)

    return render(request, 'core/search.html', {
        'tours': tours,
        'destinations': destinations,
        'query': query,
        'selected_destination': destination_slug,
        'selected_duration': duration,
    })

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            _, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if created:
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            else:
                messages.info(request, 'You are already subscribed.')
        else:
            messages.error(request, 'Please provide a valid email.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
