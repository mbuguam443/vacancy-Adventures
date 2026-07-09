from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Destination, TourPackage, TourImage

def destination_list(request):
    destinations = Destination.objects.filter(status='published')
    return render(request, 'tours/destination_list.html', {'destinations': destinations})

def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug, status='published')
    tours = TourPackage.objects.filter(destination=destination, status='published')
    return render(request, 'tours/destination_detail.html', {
        'destination': destination,
        'tours': tours,
    })

def tour_list(request):
    tours_list = TourPackage.objects.filter(status='published').order_by('-created_at')

    category = request.GET.get('category', '')
    destination_slug = request.GET.get('destination', '')
    difficulty = request.GET.get('difficulty', '')
    sort = request.GET.get('sort', '-created_at')
    query = request.GET.get('q', '')

    if category:
        tours_list = tours_list.filter(category=category)
    if destination_slug:
        tours_list = tours_list.filter(destination__slug=destination_slug)
    if difficulty:
        tours_list = tours_list.filter(difficulty=difficulty)
    if query:
        tours_list = tours_list.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    valid_sorts = ['price', '-price', 'duration_days', '-duration_days', 'title', '-title', 'created_at', '-created_at']
    if sort in valid_sorts:
        tours_list = tours_list.order_by(sort)

    paginator = Paginator(tours_list, 9)
    page = request.GET.get('page', 1)
    try:
        tours = paginator.page(page)
    except PageNotAnInteger:
        tours = paginator.page(1)
    except EmptyPage:
        tours = paginator.page(paginator.num_pages)

    destinations = Destination.objects.filter(status='published')
    context = {
        'tours': tours,
        'destinations': destinations,
        'current_category': category,
        'current_destination': destination_slug,
        'current_difficulty': difficulty,
        'current_sort': sort,
        'query': query,
    }
    return render(request, 'tours/tour_list.html', context)

def tour_detail(request, slug):
    tour = get_object_or_404(TourPackage, slug=slug, status='published')
    tour_images = tour.images.all()
    main_image = tour_images.filter(is_main=True).first() or tour_images.first()
    reviews = tour.reviews.filter(is_active=True)
    similar_tours = TourPackage.objects.filter(
        category=tour.category, status='published'
    ).exclude(id=tour.id)[:3]
    
    included = [s.strip() for s in tour.included_services.split('\n') if s.strip()] if tour.included_services else []
    excluded = [s.strip() for s in tour.excluded_services.split('\n') if s.strip()] if tour.excluded_services else []
    itinerary = [s.strip() for s in tour.itinerary.split('\n') if s.strip()] if tour.itinerary else []

    context = {
        'tour': tour,
        'main_image': main_image,
        'tour_images': tour_images,
        'reviews': reviews,
        'similar_tours': similar_tours,
        'included': included,
        'excluded': excluded,
        'itinerary': itinerary,
        'avg_rating': tour.average_rating(),
        'review_count': tour.review_count(),
    }
    return render(request, 'tours/tour_detail.html', context)
