from django.shortcuts import render
from rest_framework import viewsets
from .models import Booking, Listing
from .serializers import BookingSerializer, ListingSerializer
from rest_framework import permissions


# Create your views here.
class BookingViews(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListingViews(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]
