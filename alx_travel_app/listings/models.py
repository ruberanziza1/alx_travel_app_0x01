from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


# Create your models here.
class Listing(models.Model):
    """Model representing a property listing"""

    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('condo', 'Condominium'),
        ('cabin', 'Cabin'),
        ('hotel', 'Hotel'),
        ('resort', 'Resort'),
    ]

    listing_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    host = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    amenities = models.JSONField(default=list, blank=True)
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default='apartment'
    )
    max_guests = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    availability = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['property_type']),
            models.Index(fields=['availability']),
            models.Index(fields=['price_per_night']),
        ]

    def __str__(self):
        return f"{self.title} - {self.location}"

    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(
                reviews), 1)
        return 0

    @property
    def review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()


class Booking(models.Model):
    """Model representing a booking for a listing"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    booking_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    property = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['check_in', 'check_out']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F('check_in')),
                name='check_out_after_check_in'
            ),
        ]

    def __str__(self):
        return f"Booking {self.booking_id} - {self.property.title}"

    @property
    def duration_days(self):
        """Calculate booking duration in days"""
        return (self.check_out - self.check_in).days

    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError

        if self.check_out <= self.check_in:
            raise ValidationError(
                'Check-out date must be after check-in date.')

        if self.guests > self.property.max_guests:
            raise ValidationError(f'Number of guests ({
                self.guests}) exceeds maximum allowed ({
                    self.property.max_guests}).')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    """Model representing a review for a listing"""

    review_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    property = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['property', 'user'],
                name='unique_user_property_review'
            ),
        ]

    def __str__(self):
        return f"Review by {self.user.username} for {self.property.title} - {
            self.rating}/5"
