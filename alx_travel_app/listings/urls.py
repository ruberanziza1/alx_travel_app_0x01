from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViews, ListingViews


router = DefaultRouter()
router.register(r'listings', ListingViews, basename='lising')
router.register(r'bookings', BookingViews, basename='booking')
path('api/', include(router.urls))
