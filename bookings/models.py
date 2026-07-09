from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from tours.models import TourPackage

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    tour = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='bookings')
    travel_date = models.DateField()
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    special_requests = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f'{self.user.username} - {self.tour.title} ({self.status})'

    def total_guests(self):
        return self.adults + self.children

    def get_absolute_url(self):
        return reverse('bookings:booking_detail', args=[self.id])

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    tour = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'tour']

    def __str__(self):
        return f'{self.user.username} - {self.tour.title} ({self.rating}/5)'
