from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review
from decimal import Decimal


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Review
        fields = [
            'review_id', 'property', 'user', 'user_id', 'rating',
            'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at']

    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5.")
        return value


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model"""

    host = UserSerializer(read_only=True)
    host_id = serializers.IntegerField(write_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = [
            'listing_id', 'host', 'host_id', 'title', 'description'
            'location', 'price_per_night', 'amenities', 'property_type',
            'max_guests', 'bedrooms', 'bathrooms', 'availability',
            'created_at', 'updated_at', 'reviews', 'average_rating',
            'review_count'
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at']

    def validate_price_per_night(self, value):
        """Validate price is positive"""
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "Price per night must be greater than 0.")
        return value

    def validate_max_guests(self, value):
        """Validate max guests is positive"""
        if value < 1:
            raise serializers.ValidationError(
                "Maximum guests must be at least 1.")
        return value


class ListingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing list views"""

    host = UserSerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = [
            'listing_id', 'host', 'title', 'location', 'price_per_night',
            'property_type', 'max_guests', 'bedrooms', 'bathrooms',
            'availability', 'average_rating', 'review_count'
        ]


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""

    property = ListingListSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True, source='property')
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'booking_id', 'property', 'property_id', 'user', 'user_id',
            'check_in', 'check_out', 'guests', 'total_price', 'status',
            'created_at', 'updated_at', 'duration_days'
        ]
        read_only_fields = ['booking_id', 'created_at', 'updated_at']

    def validate(self, data):
        """Custom validation for booking dates and guests"""
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        guests = data.get('guests')
        property_obj = data.get('property')

        # Validate dates
        if check_out <= check_in:
            raise serializers.ValidationError({
                'check_out': 'Check-out date must be after check-in date.'
            })

        # Validate guests count
        if property_obj and guests > property_obj.max_guests:
            raise serializers.ValidationError({
                'guests': f'Number of guests ({
                    guests}) exceeds maximum allowed ({
                        property_obj.max_guests}).'
            })

        # Check if property is available
        if property_obj and not property_obj.availability:
            raise serializers.ValidationError({
                'property': 'This property is '
                'not currently available for booking.'
            })

        return data

    def validate_guests(self, value):
        """Validate guests count is positive"""
        if value < 1:
            raise serializers.ValidationError(
                "Number of guests must be at least 1.")
        return value

    def validate_total_price(self, value):
        """Validate total price is positive"""
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "Total price must be greater than 0.")
        return value


class BookingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for booking list views"""

    property = ListingListSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'booking_id', 'property', 'user', 'check_in', 'check_out',
            'guests', 'total_price', 'status', 'duration_days', 'created_at'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings with automatic price calculation"""

    property_id = serializers.UUIDField(source='property')

    class Meta:
        model = Booking
        fields = [
            'property_id', 'check_in', 'check_out', 'guests'
        ]

    def validate(self, data):
        """Validate and calculate total price"""
        validated_data = super().validate(data)

        property_obj = validated_data['property']
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']

        # Calculate duration and total price
        duration = (check_out - check_in).days
        total_price = property_obj.price_per_night * duration
        validated_data['total_price'] = total_price

        return validated_data

    def create(self, validated_data):
        """Create booking with calculated total price"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
