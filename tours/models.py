from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Destination(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published')]
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    featured_image = models.ImageField(upload_to='destinations/')
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    best_season = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    address = models.CharField(max_length=300, blank=True)
    rating = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    capacity = models.IntegerField(default=4)
    vehicle_type = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class TourGuide(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='guides/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    experience_years = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class TourPackage(models.Model):
    DIFFICULTY_CHOICES = [('easy', 'Easy'), ('moderate', 'Moderate'), ('challenging', 'Challenging')]
    CATEGORY_CHOICES = [
        ('safari', 'Safari'), ('beach', 'Beach'), ('cultural', 'Cultural'),
        ('adventure', 'Adventure'), ('wildlife', 'Wildlife'), ('luxury', 'Luxury'),
    ]
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published')]

    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, related_name='tours')
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    duration_days = models.IntegerField()
    duration_nights = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    max_guests = models.IntegerField(default=20)
    available_seats = models.IntegerField(default=20)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='moderate')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='safari')
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True, related_name='tours')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='tours')
    guide = models.ForeignKey(TourGuide, on_delete=models.SET_NULL, null=True, blank=True, related_name='tours')
    included_services = models.TextField(blank=True, help_text='List items separated by newline')
    excluded_services = models.TextField(blank=True, help_text='List items separated by newline')
    image = models.ImageField(upload_to='tours/', blank=True, null=True, help_text='Main tour image (shown in listings). Individual gallery images below.')
    meeting_point = models.CharField(max_length=500, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    itinerary = models.TextField(blank=True, help_text='Day-by-day itinerary')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tour_detail', args=[self.slug])

    def average_rating(self):
        reviews = self.reviews.filter(is_active=True)
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def review_count(self):
        return self.reviews.filter(is_active=True).count()

class TourDate(models.Model):
    tour = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='tour_dates')
    date = models.DateField(help_text='Available departure date')
    available_seats = models.IntegerField(help_text='Seats available for this date')
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Optional price +/- for this date')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['date']
        unique_together = ['tour', 'date']

    def __str__(self):
        return f'{self.tour.title} - {self.date} ({self.available_seats} seats)'

class TourImage(models.Model):
    tour = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/')
    caption = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_main']

    def __str__(self):
        return f'{self.tour.title} Image'
