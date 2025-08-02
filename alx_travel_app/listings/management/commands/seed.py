from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from decimal import Decimal
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listings',
            type=int,
            default=20,
            help='Number of listings to create (default: 20)'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create (default: 10)'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=30,
            help='Number of bookings to create (default: 30)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=50,
            help='Number of reviews to create (default: 50)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(
                self.style.WARNING('Clearing existing data...')
            )
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating sample data...')

        # Create users
        users = self.create_users(options['users'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(users)} users')
        )

        # Create listings
        listings = self.create_listings(users, options['listings'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(listings)} listings')
        )

        # Create bookings
        bookings = self.create_bookings(users, listings, options['bookings'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(bookings)} bookings')
        )

        # Create reviews
        reviews = self.create_reviews(users, listings, options['reviews'])
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(reviews)} reviews')
        )

        self.stdout.write(
            self.style.SUCCESS('Database seeding completed successfully!')
        )

    def create_users(self, count):
        """Create sample users"""
        users = []
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Chris', 
            'Lisa', 'Robert', 'Maria', 'James', 'Anna', 'William', 'Emily'
        ]
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 
            'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez'
        ]

        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{i+1}"
            email = f"{username}@example.com"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                }
            )
            users.append(user)

        return users

    def create_listings(self, users, count):
        """Create sample listings"""
        listings = []

        sample_data = [
            {
                'title': 'Cozy Downtown Apartment',
                'description': 'Beautiful apartment in the heart of the city with modern amenities and stunning views.',
                'location': 'New York, NY',
                'price_per_night': Decimal('120.00'),
                'property_type': 'apartment',
                'amenities': ['WiFi', 'Kitchen', 'Air Conditioning', 'Parking']
            },
            {
                'title': 'Beachfront Villa Paradise',
                'description': 'Luxurious villa with private beach access and ocean views. Perfect for family vacations.',
                'location': 'Miami, FL',
                'price_per_night': Decimal('350.00'),
                'property_type': 'villa',
                'amenities': ['Pool', 'Beach Access', 'WiFi', 'Kitchen', 'BBQ Grill']
            },
            {
                'title': 'Mountain Cabin Retreat',
                'description': 'Rustic cabin nestled in the mountains. Great for hiking and outdoor activities.',
                'location': 'Aspen, CO',
                'price_per_night': Decimal('200.00'),
                'property_type': 'cabin',
                'amenities': ['Fireplace', 'Hot Tub', 'WiFi', 'Kitchen']
            },
            {
                'title': 'Modern City Loft',
                'description': 'Stylish loft in trendy neighborhood with exposed brick and high ceilings.',
                'location': 'San Francisco, CA',
                'price_per_night': Decimal('180.00'),
                'property_type': 'apartment',
                'amenities': ['WiFi', 'Kitchen', 'Workspace', 'Gym Access']
            },
            {
                'title': 'Historic Townhouse',
                'description': 'Charming historic home with period features and modern conveniences.',
                'location': 'Boston, MA',
                'price_per_night': Decimal('160.00'),
                'property_type': 'house',
                'amenities': ['WiFi', 'Kitchen', 'Garden', 'Parking']
            }
        ]

        cities = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
            'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA',
            'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Jacksonville, FL',
            'Miami, FL', 'Seattle, WA', 'Denver, CO', 'Boston, MA'
        ]

        property_types = ['apartment', 'house', 'villa', 'condo', 'cabin']

        for i in range(count):
            if i < len(sample_data):
                data = sample_data[i]
            else:
                data = {
                    'title': f'Sample Property {i+1}',
                    'description': f'A wonderful place to stay in a great location. Property {i+1} offers comfort and convenience.',
                    'location': random.choice(cities),
                    'price_per_night': Decimal(str(random.randint(50, 400))),
                    'property_type': random.choice(property_types),
                    'amenities': random.sample([
                        'WiFi', 'Kitchen', 'Air Conditioning', 'Heating',
                        'Pool', 'Gym', 'Parking', 'Balcony', 'Garden',
                        'Hot Tub', 'Fireplace', 'BBQ Grill'
                    ], k=random.randint(2, 6))
                }

            listing = Listing.objects.create(
                host=random.choice(users),
                title=data['title'],
                description=data['description'],
                location=data['location'],
                price_per_night=data['price_per_night'],
                property_type=data['property_type'],
                amenities=data['amenities'],
                max_guests=random.randint(1, 8),
                bedrooms=random.randint(1, 4),
                bathrooms=random.randint(1, 3),
                availability=random.choice([True, True, True, False])  # 75% available
            )
            listings.append(listing)

        return listings

    def create_bookings(self, users, listings, count):
        """Create sample bookings"""
        bookings = []
        statuses = ['pending', 'confirmed', 'cancelled', 'completed']

        for i in range(count):
            property_obj = random.choice(listings)
            user = random.choice([u for u in users if u != property_obj.host])

            # Generate random dates
            start_date = date.today() + timedelta(days=random.randint(-30, 60))
            duration = random.randint(1, 14)
            end_date = start_date + timedelta(days=duration)

            guests = random.randint(1, min(property_obj.max_guests, 6))
            total_price = property_obj.price_per_night * duration

            booking = Booking.objects.create(
                property=property_obj,
                user=user,
                check_in=start_date,
                check_out=end_date,
                guests=guests,
                total_price=total_price,
                status=random.choice(statuses)
            )
            bookings.append(booking)

        return bookings

    def create_reviews(self, users, listings, count):
        """Create sample reviews"""
        reviews = []

        sample_comments = [
            "Absolutely loved this place! The host was incredibly welcoming and the location was perfect.",
            "Great value for money. Clean, comfortable, and well-equipped. Would definitely stay again.",
            "The property exceeded our expectations. Beautiful views and excellent amenities.",
            "Perfect for our family vacation. Kids loved the pool and we enjoyed the peaceful atmosphere.",
            "Convenient location with easy access to public transport. Highly recommended!",
            "Cozy and comfortable accommodation. The host provided excellent local recommendations.",
            "Everything was as described. Clean, modern, and in a great neighborhood.",
            "Outstanding hospitality! The property was immaculate and had everything we needed.",
            "Lovely place with character. Great for a romantic getaway. Will be back!",
            "Excellent communication from the host. The property was exactly what we were looking for."
        ]

        user_property_combinations = set()

        for i in range(count):
            # Ensure unique user-property combinations
            attempts = 0
            while attempts < 50:  # Avoid infinite loop
                user = random.choice(users)
                property_obj = random.choice(listings)

                # Don't let hosts review their own properties
                if user != property_obj.host:
                    combination = (user.id, property_obj.listing_id)
                    if combination not in user_property_combinations:
                        user_property_combinations.add(combination)
                        break
                attempts += 1
            else:
                continue  # Skip if no valid combination found

            rating = random.choices(
                [1, 2, 3, 4, 5],
                weights=[5, 10, 15, 35, 35]  # Weighted towards higher ratings
            )[0]

            review = Review.objects.create(
                property=property_obj,
                user=user,
                rating=rating,
                comment=random.choice(sample_comments)
            )
            reviews.append(review)

        return reviews
