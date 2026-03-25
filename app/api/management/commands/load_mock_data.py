"""
Management command to load mock data for testing.
Usage: python manage.py load_mock_data

Creates:
- 1 Admin user
- 2 Content Creator users
- 5 Regular users
- Various subscriptions (Free, Basic, Premium)
- 8 Topics with Flashcards and MCQs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models.models import (
    CustomUser,
    UserRole,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    Topic,
    FlashcardSet,
    Flashcard,
    MCQSet,
    MCQ,
)


class Command(BaseCommand):
    help = 'Load mock data for testing the Language Learning App'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Loading mock data...'))

        # Create Admin User
        admin, created = CustomUser.objects.get_or_create(
            email='admin@test.com',
            defaults={
                'role': UserRole.ADMIN,
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        if created:
            admin.set_password('Admin123!')
            admin.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Created Admin: admin@test.com / Admin123!'))

        # Create Content Creator Users
        creators_data = [
            {'email': 'creator1@test.com', 'first_name': 'John', 'last_name': 'Creator'},
            {'email': 'creator2@test.com', 'first_name': 'Jane', 'last_name': 'Writer'},
        ]
        for data in creators_data:
            user, created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'role': UserRole.CONTENT_CREATOR,
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_verified': True,
                }
            )
            if created:
                user.set_password('Creator123!')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created Content Creator: {data["email"]} / Creator123!'))

        # Create Regular Users
        users_data = [
            {'email': 'user1@test.com', 'first_name': 'Alice', 'last_name': 'Learner'},
            {'email': 'user2@test.com', 'first_name': 'Bob', 'last_name': 'Student'},
            {'email': 'user3@test.com', 'first_name': 'Charlie', 'last_name': 'Beginner'},
            {'email': 'user4@test.com', 'first_name': 'Diana', 'last_name': 'Enthusiast'},
            {'email': 'user5@test.com', 'first_name': 'Eve', 'last_name': 'Explorer'},
        ]
        for data in users_data:
            user, created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults={
                    'role': UserRole.USER,
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_verified': True,
                }
            )
            if created:
                user.set_password('User123!')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created User: {data["email"]} / User123!'))

        # Create Subscriptions
        subscriptions_data = [
            {'email': 'user1@test.com', 'plan': SubscriptionPlan.PREMIUM, 'days': 365},
            {'email': 'user2@test.com', 'plan': SubscriptionPlan.PREMIUM, 'days': 30},
            {'email': 'user3@test.com', 'plan': SubscriptionPlan.BASIC, 'days': 90},
            {'email': 'creator1@test.com', 'plan': SubscriptionPlan.BASIC, 'days': 180},
        ]

        for data in subscriptions_data:
            try:
                user = CustomUser.objects.get(email=data['email'])
                if not hasattr(user, 'subscription'):
                    end_date = timezone.now() + timedelta(days=data['days'])
                    Subscription.objects.create(
                        user=user,
                        plan=data['plan'],
                        status=SubscriptionStatus.ACTIVE,
                        start_date=timezone.now(),
                        end_date=end_date,
                        auto_renew=True,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Created {data["plan"]} subscription for {data["email"]}'
                    ))
            except CustomUser.DoesNotExist:
                pass

        # =========================================================================
        # CONTENT DATA - Topics, Flashcards, MCQs
        # =========================================================================
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Creating content data...'))

        # Get creator for content ownership
        creator = CustomUser.objects.get(email='creator1@test.com')

        # =============================================================================
        # TOPIC 1: Food & Dining (FREE - Basic content)
        # =============================================================================
        topic1, _ = Topic.objects.get_or_create(
            name='Food & Dining',
            defaults={
                'description': 'Learn vocabulary and phrases for restaurants, meals, and food culture.',
                'icon': '🍽️',
                'is_active': True,
                'is_premium': False,
                'order': 1,
            }
        )
        self.stdout.write(f'  ✓ Created Topic: {topic1.name} (Free)')

        # Flashcard Set 1.1: Restaurant Basics (FREE)
        fcs1_1, _ = FlashcardSet.objects.get_or_create(
            topic=topic1, name='Restaurant Basics',
            defaults={'description': 'Essential words for dining out', 'is_active': True, 'is_premium': False, 'order': 1}
        )
        flashcards_1_1 = [
            {'front': 'Menu', 'back': 'A list of food and drink options', 'hint': 'What you read at a restaurant', 'is_premium': False},
            {'front': 'Waiter', 'back': 'A person who serves food at a restaurant', 'hint': 'Someone who takes your order', 'is_premium': False},
            {'front': 'Bill/Check', 'back': 'The document showing what you owe', 'hint': 'You pay this at the end', 'is_premium': False},
            {'front': 'Tip', 'back': 'Extra money given for good service', 'hint': 'Usually 15-20%', 'is_premium': False},
            {'front': 'Reservation', 'back': 'A booking to hold a table', 'hint': 'Call ahead to make one', 'is_premium': False},
            {'front': 'Appetizer', 'back': 'A small dish served before the main course', 'hint': 'Also called starter', 'is_premium': False},
            {'front': 'Main Course', 'back': 'The primary dish of a meal', 'hint': 'The biggest part of your meal', 'is_premium': False},
            {'front': 'Dessert', 'back': 'Sweet dish served after the main course', 'hint': 'Cake, ice cream, pie', 'is_premium': False},
            {'front': 'Beverage', 'back': 'A drink', 'hint': 'Anything you drink', 'is_premium': False},
            {'front': 'Sommelier', 'back': 'A wine expert who recommends wines', 'hint': 'Premium vocabulary', 'is_premium': True},
        ]
        for i, fc in enumerate(flashcards_1_1):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs1_1,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'is_premium': fc.get('is_premium', False), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs1_1.name} ({len(flashcards_1_1)} cards)')

        # Flashcard Set 1.2: Food Items (PREMIUM - Advanced vocabulary)
        fcs1_2, _ = FlashcardSet.objects.get_or_create(
            topic=topic1, name='Food Items',
            defaults={'description': 'Common foods and ingredients', 'is_active': True, 'is_premium': True, 'order': 2}
        )
        flashcards_1_2 = [
            {'front': 'Pasta', 'back': 'Italian noodles made from wheat flour', 'hint': 'Spaghetti, linguine'},
            {'front': 'Pizza', 'back': 'Flatbread topped with cheese and toppings', 'hint': 'Popular Italian dish'},
            {'front': 'Steak', 'back': 'A thick slice of meat, usually beef', 'hint': 'Grilled or pan-fried'},
            {'front': 'Salad', 'back': 'A dish of mixed raw vegetables', 'hint': 'Healthy side dish'},
            {'front': 'Soup', 'back': 'A liquid dish made by boiling ingredients', 'hint': 'Often served warm'},
            {'front': 'Bread', 'back': 'A staple food made from flour', 'hint': 'Toast, bagel, roll'},
            {'front': 'Rice', 'back': 'A grain that is a staple in many cuisines', 'hint': 'White, brown, jasmine'},
            {'front': 'Chicken', 'back': 'The meat of a domestic fowl', 'hint': 'White meat, dark meat'},
            {'front': 'Seafood', 'back': 'Food from the sea', 'hint': 'Fish, shrimp, crab'},
            {'front': 'Vegetables', 'back': 'Edible plants', 'hint': 'Carrots, broccoli, spinach'},
        ]
        for i, fc in enumerate(flashcards_1_2):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs1_2,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs1_2.name} ({len(flashcards_1_2)} cards)')

        # MCQ Set 1.1: Dining Etiquette (FREE)
        mcqs1_1, _ = MCQSet.objects.get_or_create(
            topic=topic1, name='Dining Etiquette',
            defaults={'description': 'Politeness and manners when eating', 'is_active': True, 'is_premium': False, 'order': 1}
        )
        mcqs_1_1 = [
            {
                'question': 'What do you call the document listing food options at a restaurant?',
                'option_a': 'Bill', 'option_b': 'Menu', 'option_c': 'Recipe', 'option_d': 'Order',
                'correct_option': 'B', 'explanation': 'A menu lists the available dishes and drinks.', 'is_premium': False
            },
            {
                'question': 'When you finish eating and want to pay, you ask for the _____?',
                'option_a': 'Menu', 'option_b': 'Tip', 'option_c': 'Check/Bill', 'option_d': 'Waiter',
                'correct_option': 'C', 'explanation': 'The bill/check shows your total cost.', 'is_premium': False
            },
            {
                'question': 'Extra money given to show appreciation for service is called a _____?',
                'option_a': 'Discount', 'option_b': 'Tip', 'option_c': 'Refund', 'option_d': 'Deposit',
                'correct_option': 'B', 'explanation': 'A tip is a gratuity given for good service.', 'is_premium': False
            },
            {
                'question': 'A booking to reserve a table is called a _____?',
                'option_a': 'Reservation', 'option_b': 'Order', 'option_c': 'Appointment', 'option_d': 'Booking',
                'correct_option': 'A', 'explanation': 'A reservation holds a table for you.', 'is_premium': False
            },
            {
                'question': 'What is a small dish served before the main meal called?',
                'option_a': 'Dessert', 'option_b': 'Appetizer', 'option_c': 'Side dish', 'option_d': 'Snack',
                'correct_option': 'B', 'explanation': 'An appetizer is also called a starter.', 'is_premium': False
            },
            {
                'question': 'Who is the person who serves food and takes orders?',
                'option_a': 'Chef', 'option_b': 'Manager', 'option_c': 'Waiter', 'option_d': 'Customer',
                'correct_option': 'C', 'explanation': 'A waiter serves food to customers.', 'is_premium': False
            },
            {
                'question': 'Which course comes after the main course?',
                'option_a': 'Appetizer', 'option_b': 'Dessert', 'option_c': 'Salad', 'option_d': 'Soup',
                'correct_option': 'B', 'explanation': 'Dessert is the sweet course at the end.', 'is_premium': False
            },
            {
                'question': 'What is the French term for a small, elegant restaurant?',
                'option_a': 'Cafeteria', 'option_b': 'Bistro', 'option_c': 'Buffet', 'option_d': 'Fast Food',
                'correct_option': 'B', 'explanation': 'A bistro is a small, informal French restaurant.', 'is_premium': True
            },
        ]
        for i, mcq in enumerate(mcqs_1_1):
            MCQ.objects.get_or_create(
                mcq_set=mcqs1_1,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'is_premium': mcq.get('is_premium', False),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs1_1.name} ({len(mcqs_1_1)} questions)')

        # MCQ Set 1.2: Food Vocabulary (PREMIUM)
        mcqs1_2, _ = MCQSet.objects.get_or_create(
            topic=topic1, name='Food Vocabulary',
            defaults={'description': 'Common food and ingredient terms', 'is_active': True, 'is_premium': True, 'order': 2}
        )
        mcqs_1_2 = [
            {
                'question': 'What is pasta?',
                'option_a': 'A type of bread', 'option_b': 'Italian noodles', 'option_c': 'A meat dish', 'option_d': 'A soup',
                'correct_option': 'B', 'explanation': 'Pasta includes spaghetti, linguine, and many other noodle varieties.'
            },
            {
                'question': 'Pizza is a popular dish from which country?',
                'option_a': 'France', 'option_b': 'Spain', 'option_c': 'Italy', 'option_d': 'Greece',
                'correct_option': 'C', 'explanation': 'Pizza originated in Italy.'
            },
            {
                'question': 'What is a steak typically made from?',
                'option_a': 'Chicken', 'option_b': 'Beef', 'option_c': 'Fish', 'option_d': 'Vegetables',
                'correct_option': 'B', 'explanation': 'Steak is usually a thick cut of beef.'
            },
            {
                'question': 'A salad is primarily made of:',
                'option_a': 'Meat', 'option_b': 'Vegetables', 'option_c': 'Cheese', 'option_d': 'Bread',
                'correct_option': 'B', 'explanation': 'Salads are typically made from raw vegetables.'
            },
            {
                'question': 'What is rice?',
                'option_a': 'A type of meat', 'option_b': 'A grain', 'option_c': 'A vegetable', 'option_d': 'A fruit',
                'correct_option': 'B', 'explanation': 'Rice is a grain that is a staple in many cuisines.'
            },
            {
                'question': 'Seafood includes all of the following EXCEPT:',
                'option_a': 'Shrimp', 'option_b': 'Crab', 'option_c': 'Chicken', 'option_d': 'Fish',
                'correct_option': 'C', 'explanation': 'Chicken is not seafood - it is poultry.'
            },
            {
                'question': 'Soup is best described as:',
                'option_a': 'A dry dish', 'option_b': 'A liquid dish', 'option_c': 'A frozen dish', 'option_d': 'A raw dish',
                'correct_option': 'B', 'explanation': 'Soup is a liquid dish made by boiling ingredients.'
            },
            {
                'question': 'What are vegetables?',
                'option_a': 'Edible plants', 'option_b': 'Edible animals', 'option_c': 'Edible minerals', 'option_d': 'Edible fungi',
                'correct_option': 'A', 'explanation': 'Vegetables are edible plants like carrots, broccoli, etc.'
            },
        ]
        for i, mcq in enumerate(mcqs_1_2):
            MCQ.objects.get_or_create(
                mcq_set=mcqs1_2,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs1_2.name} ({len(mcqs_1_2)} questions)')

        # =============================================================================
        # TOPIC 2: Travel (FREE - Basic content)
        # =============================================================================
        topic2, _ = Topic.objects.get_or_create(
            name='Travel',
            defaults={
                'description': 'Essential vocabulary and phrases for traveling abroad.',
                'icon': '✈️',
                'is_active': True,
                'is_premium': False,
                'order': 2,
            }
        )
        self.stdout.write(f'  ✓ Created Topic: {topic2.name} (Free)')

        # Flashcard Set 2.1: Airport & Flights (PREMIUM)
        fcs2_1, _ = FlashcardSet.objects.get_or_create(
            topic=topic2, name='Airport & Flights',
            defaults={'description': 'Words related to air travel', 'is_active': True, 'is_premium': True, 'order': 1}
        )
        flashcards_2_1 = [
            {'front': 'Boarding Pass', 'back': 'A document that allows you to board a flight', 'hint': 'You need this to get on the plane'},
            {'front': 'Gate', 'back': 'The area where passengers board their flight', 'hint': 'Find your gate number on the board'},
            {'front': 'Terminal', 'back': 'A building at an airport for passengers', 'hint': 'Large airports have multiple terminals'},
            {'front': 'Departure', 'back': 'The act of leaving or the time a flight leaves', 'hint': 'Opposite of arrival'},
            {'front': 'Arrival', 'back': 'The act of coming to a destination', 'hint': 'When the plane lands'},
            {'front': 'Baggage/Luggage', 'back': 'Bags and suitcases for travel', 'hint': 'Check-in or carry-on'},
            {'front': 'Layover', 'back': 'A stop between connecting flights', 'hint': 'You wait at the airport'},
            {'front': 'Check-in', 'back': 'The process of registering for a flight', 'hint': 'You get your boarding pass here'},
            {'front': 'Security', 'back': 'The area where passengers are screened', 'hint': 'You go through this before boarding'},
            {'front': 'Customs', 'back': 'The area for declaring goods when entering a country', 'hint': 'Declare your items here'},
        ]
        for i, fc in enumerate(flashcards_2_1):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs2_1,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs2_1.name} ({len(flashcards_2_1)} cards)')

        # Flashcard Set 2.2: Hotel & Accommodation
        fcs2_2, _ = FlashcardSet.objects.get_or_create(
            topic=topic2, name='Hotel & Accommodation',
            defaults={'description': 'Words for staying at hotels', 'is_active': True, 'order': 2}
        )
        flashcards_2_2 = [
            {'front': 'Reservation', 'back': 'A booking to hold a room', 'hint': 'Book in advance'},
            {'front': 'Reception/Front Desk', 'back': 'The area where you check in', 'hint': 'First place you go'},
            {'front': 'Check-in', 'back': 'The process of registering at a hotel', 'hint': 'Give your name and get a key'},
            {'front': 'Check-out', 'back': 'The process of leaving a hotel', 'hint': 'Pay and return the key'},
            {'front': 'Suite', 'back': 'A luxurious room with multiple areas', 'hint': 'More than a standard room'},
            {'front': 'Single Room', 'back': 'A room for one person', 'hint': 'One bed'},
            {'front': 'Double Room', 'back': 'A room with a double bed', 'hint': 'Two people'},
            {'front': 'Breakfast', 'back': 'The first meal of the day', 'hint': 'Often included'},
            {'front': 'WiFi', 'back': 'Wireless internet connection', 'hint': 'Free at many hotels'},
            {'front': 'Amenities', 'back': 'Facilities and services provided', 'hint': 'Pool, gym, restaurant'},
        ]
        for i, fc in enumerate(flashcards_2_2):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs2_2,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs2_2.name} ({len(flashcards_2_2)} cards)')

        # MCQ Set 2.1: Airport Vocabulary (PREMIUM)
        mcqs2_1, _ = MCQSet.objects.get_or_create(
            topic=topic2, name='Airport Vocabulary',
            defaults={'description': 'Terms for air travel', 'is_active': True, 'is_premium': True, 'order': 1}
        )
        mcqs_2_1 = [
            {
                'question': 'What document allows you to board an airplane?',
                'option_a': 'Passport', 'option_b': 'Boarding Pass', 'option_c': 'Ticket', 'option_d': 'Visa',
                'correct_option': 'B', 'explanation': 'A boarding pass is required to enter the plane.'
            },
            {
                'question': 'The area where you board your flight is called a _____?',
                'option_a': 'Terminal', 'option_b': 'Gate', 'option_c': 'Lobby', 'option_d': 'Platform',
                'correct_option': 'B', 'explanation': 'Gates are numbered areas where passengers board.'
            },
            {
                'question': 'A stop between connecting flights is called a _____?',
                'option_a': 'Stopover', 'option_b': 'Layover', 'option_c': 'Transit', 'option_d': 'Delay',
                'correct_option': 'B', 'explanation': 'A layover is when you wait at an airport between flights.'
            },
            {
                'question': 'The process of registering for a flight is called _____?',
                'option_a': 'Check-out', 'option_b': 'Check-in', 'option_c': 'Boarding', 'option_d': 'Departure',
                'correct_option': 'B', 'explanation': 'Check-in is where you get your boarding pass and bags.'
            },
            {
                'question': 'Where do passengers get screened before boarding?',
                'option_a': 'Customs', 'option_b': 'Security', 'option_c': 'Gate', 'option_d': 'Terminal',
                'correct_option': 'B', 'explanation': 'Security screening checks for prohibited items.'
            },
            {
                'question': 'What is the time a flight leaves called?',
                'option_a': 'Arrival', 'option_b': 'Departure', 'option_c': 'Landing', 'option_d': 'Takeoff',
                'correct_option': 'B', 'explanation': 'Departure is when the plane leaves.'
            },
            {
                'question': 'Your bags and suitcases are called _____?',
                'option_a': 'Cargo', 'option_b': 'Baggage/Luggage', 'option_c': 'Freight', 'option_d': 'Parcel',
                'correct_option': 'B', 'explanation': 'Baggage or luggage refers to your travel bags.'
            },
            {
                'question': 'When entering a new country, you go through _____?',
                'option_a': 'Security', 'option_b': 'Customs', 'option_c': 'Check-in', 'option_d': 'Boarding',
                'correct_option': 'B', 'explanation': 'Customs is where you declare goods when entering a country.'
            },
        ]
        for i, mcq in enumerate(mcqs_2_1):
            MCQ.objects.get_or_create(
                mcq_set=mcqs2_1,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs2_1.name} ({len(mcqs_2_1)} questions)')

        # MCQ Set 2.2: Hotel Vocabulary
        mcqs2_2, _ = MCQSet.objects.get_or_create(
            topic=topic2, name='Hotel Vocabulary',
            defaults={'description': 'Terms for hotel stays', 'is_active': True, 'order': 2}
        )
        mcqs_2_2 = [
            {
                'question': 'The area where you check in at a hotel is called _____?',
                'option_a': 'Lobby', 'option_b': 'Reception/Front Desk', 'option_c': 'Room Service', 'option_d': 'Concierge',
                'correct_option': 'B', 'explanation': 'The front desk is where you register and get your room key.'
            },
            {
                'question': 'A room for one person is called a _____ room?',
                'option_a': 'Double', 'option_b': 'Single', 'option_c': 'Suite', 'option_d': 'Twin',
                'correct_option': 'B', 'explanation': 'A single room has one bed for one person.'
            },
            {
                'question': 'A luxurious room with multiple areas is called a _____?',
                'option_a': 'Single', 'option_b': 'Double', 'option_c': 'Suite', 'option_d': 'Standard',
                'correct_option': 'C', 'explanation': 'A suite is a large, luxurious hotel room.'
            },
            {
                'question': 'The process of leaving a hotel and paying is called _____?',
                'option_a': 'Check-in', 'option_b': 'Check-out', 'option_c': 'Departure', 'option_d': 'Exit',
                'correct_option': 'B', 'explanation': 'Check-out is when you leave the hotel.'
            },
            {
                'question': 'The first meal of the day is called _____?',
                'option_a': 'Lunch', 'option_b': 'Dinner', 'option_c': 'Breakfast', 'option_d': 'Supper',
                'correct_option': 'C', 'explanation': 'Breakfast is eaten in the morning.'
            },
            {
                'question': 'Wireless internet at a hotel is called _____?',
                'option_a': 'Ethernet', 'option_b': 'WiFi', 'option_c': 'Bluetooth', 'option_d': 'LAN',
                'correct_option': 'B', 'explanation': 'WiFi is wireless internet connection.'
            },
            {
                'question': 'Facilities like pool, gym, and restaurant are called _____?',
                'option_a': 'Services', 'option_b': 'Amenities', 'option_c': 'Features', 'option_d': 'Options',
                'correct_option': 'B', 'explanation': 'Amenities are the facilities and services provided.'
            },
            {
                'question': 'A booking to hold a room is called a _____?',
                'option_a': 'Appointment', 'option_b': 'Reservation', 'option_c': 'Schedule', 'option_d': 'Plan',
                'correct_option': 'B', 'explanation': 'A reservation holds a room for you.'
            },
        ]
        for i, mcq in enumerate(mcqs_2_2):
            MCQ.objects.get_or_create(
                mcq_set=mcqs2_2,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs2_2.name} ({len(mcqs_2_2)} questions)')

        # =============================================================================
        # TOPIC 3: Business (PREMIUM - Professional content)
        # =============================================================================
        topic3, _ = Topic.objects.get_or_create(
            name='Business',
            defaults={
                'description': 'Professional vocabulary for workplace and business communication.',
                'icon': '💼',
                'is_active': True,
                'is_premium': True,
                'order': 3,
            }
        )
        self.stdout.write(f'  ✓ Created Topic: {topic3.name} (Premium)')

        # Flashcard Set 3.1: Office Essentials
        fcs3_1, _ = FlashcardSet.objects.get_or_create(
            topic=topic3, name='Office Essentials',
            defaults={'description': 'Common office words and phrases', 'is_active': True, 'order': 1}
        )
        flashcards_3_1 = [
            {'front': 'Deadline', 'back': 'A date or time by which something must be completed', 'hint': 'Time pressure'},
            {'front': 'Meeting', 'back': 'A gathering of people to discuss something', 'hint': 'Conference room'},
            {'front': 'Colleague', 'back': 'A person you work with', 'hint': 'Coworker'},
            {'front': 'Manager', 'back': 'A person who supervises others', 'hint': 'Boss'},
            {'front': 'Project', 'back': 'A planned undertaking with a goal', 'hint': 'Team work'},
            {'front': 'Budget', 'back': 'The amount of money available', 'hint': 'Financial plan'},
            {'front': 'Presentation', 'back': 'A talk showing information', 'hint': 'Slides, projector'},
            {'front': 'Email', 'back': 'Electronic mail', 'hint': 'Send messages online'},
            {'front': 'Report', 'back': 'A written document with information', 'hint': 'Data and analysis'},
            {'front': 'Schedule', 'back': 'A plan for events and times', 'hint': 'Calendar'},
        ]
        for i, fc in enumerate(flashcards_3_1):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs3_1,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs3_1.name} ({len(flashcards_3_1)} cards)')

        # Flashcard Set 3.2: Business Meetings
        fcs3_2, _ = FlashcardSet.objects.get_or_create(
            topic=topic3, name='Business Meetings',
            defaults={'description': 'Phrases for meetings and discussions', 'is_active': True, 'order': 2}
        )
        flashcards_3_2 = [
            {'front': 'Agenda', 'back': 'A list of topics to discuss', 'hint': 'Meeting plan'},
            {'front': 'Minutes', 'back': 'Written record of a meeting', 'hint': 'Notes taken'},
            {'front': 'Action Items', 'back': 'Tasks assigned to be completed', 'hint': 'Follow-up tasks'},
            {'front': 'Follow Up', 'back': 'To check on something later', 'hint': 'Get back to'},
            {'front': 'Consensus', 'back': 'General agreement', 'hint': 'Everyone agrees'},
            {'front': 'Brainstorm', 'back': 'Generate ideas together', 'hint': 'Creative session'},
            {'front': 'Facilitate', 'back': 'To guide a discussion', 'hint': 'Lead the talk'},
            {'front': 'Delegate', 'back': 'Assign tasks to others', 'hint': 'Give responsibility'},
            {'front': 'Prioritize', 'back': 'Rank tasks by importance', 'hint': 'What is most important'},
            {'front': 'Feedback', 'back': 'Information about performance', 'hint': 'Constructive criticism'},
        ]
        for i, fc in enumerate(flashcards_3_2):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs3_2,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs3_2.name} ({len(flashcards_3_2)} cards)')

        # MCQ Set 3.1: Business Terms
        mcqs3_1, _ = MCQSet.objects.get_or_create(
            topic=topic3, name='Business Terms',
            defaults={'description': 'Common business vocabulary', 'is_active': True, 'order': 1}
        )
        mcqs_3_1 = [
            {
                'question': 'A date by which work must be finished is called a _____?',
                'option_a': 'Schedule', 'option_b': 'Deadline', 'option_c': 'Plan', 'option_d': 'Goal',
                'correct_option': 'B', 'explanation': 'A deadline is the final date for completion.'
            },
            {
                'question': 'A gathering of people to discuss business is called a _____?',
                'option_a': 'Party', 'option_b': 'Meeting', 'option_c': 'Lecture', 'option_d': 'Class',
                'correct_option': 'B', 'explanation': 'A meeting is a business gathering.'
            },
            {
                'question': 'A person you work with is called a _____?',
                'option_a': 'Manager', 'option_b': 'Colleague', 'option_c': 'Customer', 'option_d': 'Client',
                'correct_option': 'B', 'explanation': 'A colleague is a coworker.'
            },
            {
                'question': 'A talk with slides showing information is called a _____?',
                'option_a': 'Report', 'option_b': 'Presentation', 'option_c': 'Email', 'option_d': 'Conversation',
                'correct_option': 'B', 'explanation': 'A presentation uses slides to share information.'
            },
            {
                'question': 'Electronic mail is commonly called _____?',
                'option_a': 'Letter', 'option_b': 'Email', 'option_c': 'Fax', 'option_d': 'Memo',
                'correct_option': 'B', 'explanation': 'Email is electronic mail.'
            },
            {
                'question': 'A written document with information and data is a _____?',
                'option_a': 'Letter', 'option_b': 'Report', 'option_c': 'Email', 'option_d': 'Note',
                'correct_option': 'B', 'explanation': 'A report is a formal written document.'
            },
            {
                'question': 'A plan of events and times is called a _____?',
                'option_a': 'Budget', 'option_b': 'Schedule', 'option_c': 'Report', 'option_d': 'List',
                'correct_option': 'B', 'explanation': 'A schedule plans when things happen.'
            },
            {
                'question': 'The amount of money available for a project is called the _____?',
                'option_a': 'Schedule', 'option_b': 'Budget', 'option_c': 'Report', 'option_d': 'Plan',
                'correct_option': 'B', 'explanation': 'A budget is financial planning for money.'
            },
        ]
        for i, mcq in enumerate(mcqs_3_1):
            MCQ.objects.get_or_create(
                mcq_set=mcqs3_1,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs3_1.name} ({len(mcqs_3_1)} questions)')

        # =============================================================================
        # TOPIC 4: Everyday Conversation (FREE - Basic content)
        # =============================================================================
        topic4, _ = Topic.objects.get_or_create(
            name='Everyday Conversation',
            defaults={
                'description': 'Common phrases and expressions for daily interactions.',
                'icon': '💬',
                'is_active': True,
                'is_premium': False,
                'order': 4,
            }
        )
        self.stdout.write(f'  ✓ Created Topic: {topic4.name} (Free)')

        # Flashcard Set 4.1: Greetings
        fcs4_1, _ = FlashcardSet.objects.get_or_create(
            topic=topic4, name='Greetings & Introductions',
            defaults={'description': 'How to greet and introduce yourself', 'is_active': True, 'order': 1}
        )
        flashcards_4_1 = [
            {'front': 'Hello', 'back': 'A common greeting', 'hint': 'Hi'},
            {'front': 'Good morning', 'back': 'Greeting used before noon', 'hint': 'Early in the day'},
            {'front': 'Good afternoon', 'back': 'Greeting used after noon', 'hint': 'Midday'},
            {'front': 'Good evening', 'back': 'Greeting used after 5pm', 'hint': 'Later in the day'},
            {'front': 'Goodbye', 'back': 'A farewell', 'hint': 'Bye'},
            {'front': 'See you later', 'back': 'Informal farewell', 'hint': 'See you soon'},
            {'front': "What's your name?", 'back': 'Asking someone their name', 'hint': 'Introduction'},
            {'front': 'Nice to meet you', 'back': 'Polite phrase when meeting someone', 'hint': 'First meeting'},
            {'front': 'Where are you from?', 'back': 'Asking about someone\'s origin', 'hint': 'Country or city'},
            {'front': 'How are you?', 'back': 'Asking about someone\'s wellbeing', 'hint': 'Common greeting'},
        ]
        for i, fc in enumerate(flashcards_4_1):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs4_1,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs4_1.name} ({len(flashcards_4_1)} cards)')

        # Flashcard Set 4.2: Common Phrases
        fcs4_2, _ = FlashcardSet.objects.get_or_create(
            topic=topic4, name='Common Phrases',
            defaults={'description': 'Useful everyday expressions', 'is_active': True, 'order': 2}
        )
        flashcards_4_2 = [
            {'front': 'Excuse me', 'back': 'Polite way to get attention or apologize', 'hint': 'Sorry to bother'},
            {'front': 'Thank you', 'back': 'Expression of gratitude', 'hint': 'Thanks'},
            {'front': 'You\'re welcome', 'back': 'Response to thank you', 'hint': 'No problem'},
            {'front': 'Sorry', 'back': 'Expression of apology', 'hint': 'Apologize'},
            {'front': 'Please', 'back': 'Polite request word', 'hint': 'Kindly'},
            {'front': 'I don\'t understand', 'back': 'When you need clarification', 'hint': 'Not clear'},
            {'front': 'Could you repeat that?', 'back': 'Asking someone to say again', 'hint': 'Repeat please'},
            {'front': 'How much does this cost?', 'back': 'Asking about price', 'hint': 'Price question'},
            {'front': 'Where is the bathroom?', 'back': 'Asking for directions to restroom', 'hint': 'Restroom'},
            {'front': 'I would like...', 'back': 'Polite way to request something', 'hint': 'I want'},
            {'front': 'Salutations', 'back': 'Formal greeting or expression of goodwill', 'hint': 'Premium vocabulary', 'is_premium': True},
        ]
        for i, fc in enumerate(flashcards_4_2):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs4_2,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs4_2.name} ({len(flashcards_4_2)} cards)')

        # MCQ Set 4.1: Greetings Quiz
        mcqs4_1, _ = MCQSet.objects.get_or_create(
            topic=topic4, name='Greetings Quiz',
            defaults={'description': 'Test your greeting knowledge', 'is_active': True, 'order': 1}
        )
        mcqs_4_1 = [
            {
                'question': 'What do you say when you meet someone for the first time?',
                'option_a': 'Goodbye', 'option_b': 'Nice to meet you', 'option_c': 'See you later', 'option_d': 'Good morning',
                'correct_option': 'B', 'explanation': 'Nice to meet you is appropriate for first meetings.'
            },
            {
                'question': 'What greeting do you use in the morning?',
                'option_a': 'Good evening', 'option_b': 'Good morning', 'option_c': 'Good night', 'option_d': 'Good afternoon',
                'correct_option': 'B', 'explanation': 'Good morning is used before noon.'
            },
            {
                'question': 'How do you ask someone their name?',
                'option_a': 'How are you?', 'option_b': "What's your name?", 'option_c': 'Where are you from?', 'option_d': 'How much?',
                'correct_option': 'B', 'explanation': "What's your name? asks for their name."
            },
            {
                'question': 'What do you say when leaving someone?',
                'option_a': 'Hello', 'option_b': 'Goodbye', 'option_c': 'Thank you', 'option_d': 'Sorry',
                'correct_option': 'B', 'explanation': 'Goodbye is a farewell.'
            },
            {
                'question': 'What phrase do you use to ask about someone\'s wellbeing?',
                'option_a': 'What is your name?', 'option_b': 'How are you?', 'option_c': 'Where are you from?', 'option_d': 'What time is it?',
                'correct_option': 'B', 'explanation': 'How are you? asks about wellbeing.'
            },
            {
                'question': 'Which greeting is used after 5pm?',
                'option_a': 'Good morning', 'option_b': 'Good afternoon', 'option_c': 'Good evening', 'option_d': 'Good night',
                'correct_option': 'C', 'explanation': 'Good evening is used after about 5pm.'
            },
            {
                'question': 'What do you say when you want to leave and see someone again?',
                'option_a': 'Goodbye forever', 'option_b': 'See you later', 'option_c': 'Thank you', 'option_d': 'Sorry',
                'correct_option': 'B', 'explanation': 'See you later is informal and suggests future meetings.'
            },
            {
                'question': 'What question asks about someone\'s origin?',
                'option_a': 'How are you?', 'option_b': "What's your name?", 'option_c': 'Where are you from?', 'option_d': 'How much?',
                'correct_option': 'C', 'explanation': 'Where are you from? asks about origin.'
            },
            {
                'question': 'What is a formal word for greetings or goodbyes?',
                'option_a': 'Hi', 'option_b': 'Bye', 'option_c': 'Salutations', 'option_d': 'Hey',
                'correct_option': 'C', 'explanation': 'Salutations is a formal term for greetings.', 'is_premium': True
            },
        ]
        for i, mcq in enumerate(mcqs_4_1):
            MCQ.objects.get_or_create(
                mcq_set=mcqs4_1,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs4_1.name} ({len(mcqs_4_1)} questions)')

        # =============================================================================
        # TOPIC 5: Technology (PREMIUM - Advanced content)
        # =============================================================================
        topic5, _ = Topic.objects.get_or_create(
            name='Technology',
            defaults={
                'description': 'Vocabulary for computers, internet, and digital devices.',
                'icon': '💻',
                'is_active': True,
                'is_premium': True,
                'order': 5,
            }
        )
        self.stdout.write(f'  ✓ Created Topic: {topic5.name} (Premium)')

        # Flashcard Set 5.1: Computer Basics
        fcs5_1, _ = FlashcardSet.objects.get_or_create(
            topic=topic5, name='Computer Basics',
            defaults={'description': 'Essential computer terms', 'is_active': True, 'order': 1}
        )
        flashcards_5_1 = [
            {'front': 'Keyboard', 'back': 'Input device with keys for typing', 'hint': 'Type letters'},
            {'front': 'Mouse', 'back': 'Device to move cursor on screen', 'hint': 'Click and scroll'},
            {'front': 'Monitor', 'back': 'The screen that displays images', 'hint': 'Visual output'},
            {'front': 'Software', 'back': 'Programs that run on a computer', 'hint': 'Applications'},
            {'front': 'Hardware', 'back': 'Physical parts of a computer', 'hint': 'Tangible components'},
            {'front': 'Download', 'back': 'Transfer data from internet to device', 'hint': 'Get from web'},
            {'front': 'Upload', 'back': 'Transfer data from device to internet', 'hint': 'Send to web'},
            {'front': 'File', 'back': 'A document or data stored digitally', 'hint': 'Save as'},
            {'front': 'Folder', 'back': 'Container for organizing files', 'hint': 'Directory'},
            {'front': 'Backup', 'back': 'Copy of data for protection', 'hint': 'Safety copy'},
        ]
        for i, fc in enumerate(flashcards_5_1):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs5_1,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs5_1.name} ({len(flashcards_5_1)} cards)')

        # Flashcard Set 5.2: Internet & Online
        fcs5_2, _ = FlashcardSet.objects.get_or_create(
            topic=topic5, name='Internet & Online',
            defaults={'description': 'Web and online terminology', 'is_active': True, 'order': 2}
        )
        flashcards_5_2 = [
            {'front': 'Browser', 'back': 'Software to view websites', 'hint': 'Chrome, Firefox'},
            {'front': 'Website', 'back': 'A collection of web pages', 'hint': 'Online location'},
            {'front': 'Search Engine', 'back': 'Tool to find information online', 'hint': 'Google, Bing'},
            {'front': 'Link/Hyperlink', 'back': 'Clickable text or image to another page', 'hint': 'Click here'},
            {'front': 'Password', 'back': 'Secret code to access accounts', 'hint': 'Keep it secret'},
            {'front': 'Username', 'back': 'Name used to identify a user', 'hint': 'Login name'},
            {'front': 'Email', 'back': 'Electronic mail', 'hint': 'Send messages'},
            {'front': 'Social Media', 'back': 'Platforms for sharing content', 'hint': 'Facebook, Instagram'},
            {'front': 'WiFi', 'back': 'Wireless internet connection', 'hint': 'No cable needed'},
            {'front': 'Cloud Storage', 'back': 'Storing data on remote servers', 'hint': 'Online storage'},
        ]
        for i, fc in enumerate(flashcards_5_2):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs5_2,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs5_2.name} ({len(flashcards_5_2)} cards)')

        # MCQ Set 5.1: Tech Basics
        mcqs5_1, _ = MCQSet.objects.get_or_create(
            topic=topic5, name='Tech Basics',
            defaults={'description': 'Basic technology terms', 'is_active': True, 'order': 1}
        )
        mcqs_5_1 = [
            {
                'question': 'What device has keys for typing?',
                'option_a': 'Mouse', 'option_b': 'Keyboard', 'option_c': 'Monitor', 'option_d': 'Speaker',
                'correct_option': 'B', 'explanation': 'A keyboard has keys for typing.'
            },
            {
                'question': 'What device moves the cursor on screen?',
                'option_a': 'Keyboard', 'option_b': 'Mouse', 'option_c': 'Monitor', 'option_d': 'Printer',
                'correct_option': 'B', 'explanation': 'A mouse moves the cursor.'
            },
            {
                'question': 'The screen that displays images is called a _____?',
                'option_a': 'Keyboard', 'option_b': 'Mouse', 'option_c': 'Monitor', 'option_d': 'Speaker',
                'correct_option': 'C', 'explanation': 'A monitor is the display screen.'
            },
            {
                'question': 'Programs that run on a computer are called _____?',
                'option_a': 'Hardware', 'option_b': 'Software', 'option_c': 'Firmware', 'option_d': 'Memory',
                'correct_option': 'B', 'explanation': 'Software refers to programs and applications.'
            },
            {
                'question': 'Physical parts of a computer are called _____?',
                'option_a': 'Software', 'option_b': 'Hardware', 'option_c': 'Data', 'option_d': 'Files',
                'correct_option': 'B', 'explanation': 'Hardware is the physical components.'
            },
            {
                'question': 'Transferring data from internet to your device is called _____?',
                'option_a': 'Upload', 'option_b': 'Download', 'option_c': 'Copy', 'option_d': 'Save',
                'correct_option': 'B', 'explanation': 'Download means getting data from the internet.'
            },
            {
                'question': 'A container for organizing files is called a _____?',
                'option_a': 'File', 'option_b': 'Folder', 'option_c': 'Document', 'option_d': 'Page',
                'correct_option': 'B', 'explanation': 'A folder contains and organizes files.'
            },
            {
                'question': 'A copy of data for protection is called a _____?',
                'option_a': 'File', 'option_b': 'Folder', 'option_c': 'Backup', 'option_d': 'Download',
                'correct_option': 'C', 'explanation': 'A backup protects data from loss.'
            },
        ]
        for i, mcq in enumerate(mcqs_5_1):
            MCQ.objects.get_or_create(
                mcq_set=mcqs5_1,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs5_1.name} ({len(mcqs_5_1)} questions)')

        # =============================================================================
        # TOPIC 6: Health & Wellness (PREMIUM - Medical content)
        # =============================================================================
        topic6, _ = Topic.objects.get_or_create(
            name='Health & Wellness',
            defaults={
                'description': 'Vocabulary for health, medical care, and fitness.',
                'icon': '🏥',
                'is_active': True,
                'is_premium': True,
                'order': 6,
            }
        )
        self.stdout.write(f'  ✓ Created Topic: {topic6.name} (Premium)')

        # Flashcard Set 6.1: Medical Basics
        fcs6_1, _ = FlashcardSet.objects.get_or_create(
            topic=topic6, name='Medical Basics',
            defaults={'description': 'Common medical terms', 'is_active': True, 'order': 1}
        )
        flashcards_6_1 = [
            {'front': 'Doctor', 'back': 'A medical professional who treats patients', 'hint': 'Physician'},
            {'front': 'Nurse', 'back': 'A healthcare worker who cares for patients', 'hint': 'Medical staff'},
            {'front': 'Hospital', 'back': 'A medical facility for treatment', 'hint': 'Where patients stay'},
            {'front': 'Pharmacy', 'back': 'A store that sells medicines', 'hint': 'Drug store'},
            {'front': 'Prescription', 'back': 'A written order for medicine', 'hint': 'Doctor writes this'},
            {'front': 'Symptoms', 'back': 'Signs of illness or disease', 'hint': 'What you feel'},
            {'front': 'Diagnosis', 'back': 'Identification of an illness', 'hint': 'What is wrong'},
            {'front': 'Treatment', 'back': 'Medical care for an illness', 'hint': 'Cure or therapy'},
            {'front': 'Emergency', 'back': 'A serious situation requiring immediate action', 'hint': 'Call 911'},
            {'front': 'First Aid', 'back': 'Immediate care for injuries', 'hint': 'Basic medical help'},
        ]
        for i, fc in enumerate(flashcards_6_1):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs6_1,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs6_1.name} ({len(flashcards_6_1)} cards)')

        # MCQ Set 6.1: Health Vocabulary
        mcqs6_1, _ = MCQSet.objects.get_or_create(
            topic=topic6, name='Health Vocabulary',
            defaults={'description': 'Medical and health terms', 'is_active': True, 'order': 1}
        )
        mcqs_6_1 = [
            {
                'question': 'A medical professional who treats patients is called a _____?',
                'option_a': 'Nurse', 'option_b': 'Doctor', 'option_c': 'Pharmacist', 'option_d': 'Patient',
                'correct_option': 'B', 'explanation': 'A doctor is a physician who treats patients.'
            },
            {
                'question': 'A store that sells medicines is called a _____?',
                'option_a': 'Hospital', 'option_b': 'Pharmacy', 'option_c': 'Clinic', 'option_d': 'Office',
                'correct_option': 'B', 'explanation': 'A pharmacy sells medicines and drugs.'
            },
            {
                'question': 'A written order from a doctor for medicine is a _____?',
                'option_a': 'Diagnosis', 'option_b': 'Prescription', 'option_c': 'Treatment', 'option_d': 'Symptom',
                'correct_option': 'B', 'explanation': 'A prescription is a written order for medicine.'
            },
            {
                'question': 'Signs of illness like fever or cough are called _____?',
                'option_a': 'Treatment', 'option_b': 'Diagnosis', 'option_c': 'Symptoms', 'option_d': 'Medicine',
                'correct_option': 'C', 'explanation': 'Symptoms are signs of illness.'
            },
            {
                'question': 'A medical facility where patients stay is called a _____?',
                'option_a': 'Pharmacy', 'option_b': 'Hospital', 'option_c': 'Store', 'option_d': 'Office',
                'correct_option': 'B', 'explanation': 'A hospital is a medical facility for treatment.'
            },
            {
                'question': 'Identification of an illness is called a _____?',
                'option_a': 'Symptom', 'option_b': 'Prescription', 'option_c': 'Diagnosis', 'option_d': 'Treatment',
                'correct_option': 'C', 'explanation': 'A diagnosis identifies what illness someone has.'
            },
            {
                'question': 'A healthcare worker who cares for patients is a _____?',
                'option_a': 'Doctor', 'option_b': 'Nurse', 'option_c': 'Pharmacist', 'option_d': 'Patient',
                'correct_option': 'B', 'explanation': 'A nurse provides care to patients.'
            },
            {
                'question': 'Immediate care for injuries is called _____?',
                'option_a': 'Surgery', 'option_b': 'First Aid', 'option_c': 'Treatment', 'option_d': 'Therapy',
                'correct_option': 'B', 'explanation': 'First aid is basic immediate medical care.'
            },
        ]
        for i, mcq in enumerate(mcqs_6_1):
            MCQ.objects.get_or_create(
                mcq_set=mcqs6_1,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs6_1.name} ({len(mcqs_6_1)} questions)')

        # =============================================================================
        # TOPIC 7: Sports (PREMIUM - Sports vocabulary)
        # =============================================================================
        topic7, _ = Topic.objects.get_or_create(
            name='Sports',
            defaults={
                'description': 'Vocabulary for popular sports and athletic activities.',
                'icon': '⚽',
                'is_active': True,
                'is_premium': True,
                'order': 7,
            }
        )
        self.stdout.write(f'  ✓ Created Topic: {topic7.name} (Premium)')

        # Flashcard Set 7.1: Team Sports
        fcs7_1, _ = FlashcardSet.objects.get_or_create(
            topic=topic7, name='Team Sports',
            defaults={'description': 'Sports played with teams', 'is_active': True, 'order': 1}
        )
        flashcards_7_1 = [
            {'front': 'Soccer/Football', 'back': 'A sport played with a ball and goal', 'hint': 'Most popular sport worldwide'},
            {'front': 'Basketball', 'back': 'A sport played with a ball and hoop', 'hint': 'Dunk, shoot, dribble'},
            {'front': 'Baseball', 'back': 'A sport with bat and ball', 'hint': 'Home run, inning'},
            {'front': 'Hockey', 'back': 'A sport played with a puck and sticks', 'hint': 'Ice or field'},
            {'front': 'Volleyball', 'back': 'A sport with a ball over a net', 'hint': 'Spike, set, dig'},
            {'front': 'Cricket', 'back': 'A bat and ball sport popular in Commonwealth', 'hint': 'Wicket, innings'},
            {'front': 'Rugby', 'back': 'A contact sport similar to football', 'hint': 'Try, scrum'},
            {'front': 'Tennis', 'back': 'A racquet sport played on a court', 'hint': 'Serve, volley, match'},
            {'front': 'Golf', 'back': 'A sport played with clubs and a small ball', 'hint': 'Hole in one'},
            {'front': 'Swimming', 'back': 'Moving through water using limbs', 'hint': 'Freestyle, breaststroke'},
        ]
        for i, fc in enumerate(flashcards_7_1):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs7_1,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs7_1.name} ({len(flashcards_7_1)} cards)')

        # MCQ Set 7.1: Sports Quiz
        mcqs7_1, _ = MCQSet.objects.get_or_create(
            topic=topic7, name='Sports Quiz',
            defaults={'description': 'Test your sports knowledge', 'is_active': True, 'order': 1}
        )
        mcqs_7_1 = [
            {
                'question': 'What sport is played with a ball and goal, popular worldwide?',
                'option_a': 'Basketball', 'option_b': 'Soccer/Football', 'option_c': 'Tennis', 'option_d': 'Golf',
                'correct_option': 'B', 'explanation': 'Soccer (football) is the most popular sport globally.'
            },
            {
                'question': 'What sport uses a hoop and is played with a ball?',
                'option_a': 'Soccer', 'option_b': 'Basketball', 'option_c': 'Baseball', 'option_d': 'Hockey',
                'correct_option': 'B', 'explanation': 'Basketball is played with a hoop and ball.'
            },
            {
                'question': 'What sport has a bat, ball, and bases?',
                'option_a': 'Tennis', 'option_b': 'Baseball', 'option_c': 'Golf', 'option_d': 'Cricket',
                'correct_option': 'B', 'explanation': 'Baseball uses a bat and ball on a diamond.'
            },
            {
                'question': 'What sport is played with a puck and sticks on ice?',
                'option_a': 'Soccer', 'option_b': 'Hockey', 'option_c': 'Golf', 'option_d': 'Tennis',
                'correct_option': 'B', 'explanation': 'Ice hockey is played with a puck and sticks.'
            },
            {
                'question': 'What sport has a net and is played by two teams?',
                'option_a': 'Golf', 'option_b': 'Volleyball', 'option_c': 'Tennis', 'option_d': 'Swimming',
                'correct_option': 'B', 'explanation': 'Volleyball has a net between two teams.'
            },
            {
                'question': 'What sport is played with a racquet and ball on a court?',
                'option_a': 'Golf', 'option_b': 'Tennis', 'option_c': 'Baseball', 'option_d': 'Soccer',
                'correct_option': 'B', 'explanation': 'Tennis uses racquets on a court.'
            },
            {
                'question': 'What sport uses clubs and a small ball on a course?',
                'option_a': 'Tennis', 'option_b': 'Golf', 'option_c': 'Soccer', 'option_d': 'Basketball',
                'correct_option': 'B', 'explanation': 'Golf is played with clubs on a course.'
            },
            {
                'question': 'What sport involves moving through water?',
                'option_a': 'Running', 'option_b': 'Swimming', 'option_c': 'Cycling', 'option_d': 'Jumping',
                'correct_option': 'B', 'explanation': 'Swimming is moving through water.'
            },
        ]
        for i, mcq in enumerate(mcqs_7_1):
            MCQ.objects.get_or_create(
                mcq_set=mcqs7_1,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs7_1.name} ({len(mcqs_7_1)} questions)')

        # =============================================================================
        # TOPIC 8: Nature & Environment (FREE - Basic content)
        # =============================================================================
        topic8, _ = Topic.objects.get_or_create(
            name='Nature & Environment',
            defaults={
                'description': 'Vocabulary for nature, weather, and the environment.',
                'icon': '🌿',
                'is_active': True,
                'is_premium': False,
                'order': 8,
            }
        )
        self.stdout.write(f'  ✓ Created Topic: {topic8.name} (Free)')

        # Flashcard Set 8.1: Weather
        fcs8_1, _ = FlashcardSet.objects.get_or_create(
            topic=topic8, name='Weather',
            defaults={'description': 'Weather conditions and terms', 'is_active': True, 'order': 1}
        )
        flashcards_8_1 = [
            {'front': 'Sunny', 'back': 'Weather with lots of sunshine', 'hint': 'Clear skies'},
            {'front': 'Cloudy', 'back': 'Sky covered with clouds', 'hint': 'Overcast'},
            {'front': 'Rainy', 'back': 'Weather with rain falling', 'hint': 'Wet weather'},
            {'front': 'Windy', 'back': 'Strong wind blowing', 'hint': 'Breezy'},
            {'front': 'Snowy', 'back': 'Weather with snow falling', 'hint': 'Cold weather'},
            {'front': 'Stormy', 'back': 'Weather with thunder and lightning', 'hint': 'Thunderstorm'},
            {'front': 'Foggy', 'back': 'Low visibility due to mist', 'hint': 'Hard to see'},
            {'front': 'Hot', 'back': 'High temperature', 'hint': 'Warm weather'},
            {'front': 'Cold', 'back': 'Low temperature', 'hint': 'Chilly'},
            {'front': 'Humid', 'back': 'Moist air, feels sticky', 'hint': 'Muggy'},
        ]
        for i, fc in enumerate(flashcards_8_1):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs8_1,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs8_1.name} ({len(flashcards_8_1)} cards)')

        # Flashcard Set 8.2: Nature Elements
        fcs8_2, _ = FlashcardSet.objects.get_or_create(
            topic=topic8, name='Nature Elements',
            defaults={'description': 'Natural features and elements', 'is_active': True, 'order': 2}
        )
        flashcards_8_2 = [
            {'front': 'Mountain', 'back': 'Large natural elevation of earth', 'hint': 'Tall landform'},
            {'front': 'River', 'back': 'Large flowing body of water', 'hint': 'Flows to sea'},
            {'front': 'Ocean', 'back': 'Vast body of salt water', 'hint': 'Sea'},
            {'front': 'Forest', 'back': 'Large area covered with trees', 'hint': 'Woods'},
            {'front': 'Desert', 'back': 'Dry, sandy area with little water', 'hint': 'Arid'},
            {'front': 'Beach', 'back': 'Sandy shore by the sea', 'hint': 'Coast'},
            {'front': 'Sky', 'back': 'The atmosphere above earth', 'hint': 'Blue during day'},
            {'front': 'Sun', 'back': 'The star that gives light and heat', 'hint': 'Daytime'},
            {'front': 'Moon', 'back': 'Natural satellite of earth', 'hint': 'Night time'},
            {'front': 'Stars', 'back': 'Luminous celestial bodies', 'hint': 'Twinkle at night'},
            {'front': 'Biodiversity', 'back': 'Variety of life in an ecosystem', 'hint': 'Premium vocabulary', 'is_premium': True},
        ]
        for i, fc in enumerate(flashcards_8_2):
            Flashcard.objects.get_or_create(
                flashcard_set=fcs8_2,
                front=fc['front'],
                defaults={'back': fc['back'], 'hint': fc.get('hint', ''), 'order': i}
            )
        self.stdout.write(f'    ✓ Created Flashcard Set: {fcs8_2.name} ({len(flashcards_8_2)} cards)')

        # MCQ Set 8.1: Weather Quiz
        mcqs8_1, _ = MCQSet.objects.get_or_create(
            topic=topic8, name='Weather Quiz',
            defaults={'description': 'Test your weather knowledge', 'is_active': True, 'order': 1}
        )
        mcqs_8_1 = [
            {
                'question': 'Weather with lots of sunshine is called _____?',
                'option_a': 'Cloudy', 'option_b': 'Sunny', 'option_c': 'Rainy', 'option_d': 'Windy',
                'correct_option': 'B', 'explanation': 'Sunny means clear with sunshine.'
            },
            {
                'question': 'When the sky is covered with clouds, it is _____?',
                'option_a': 'Sunny', 'option_b': 'Cloudy', 'option_c': 'Rainy', 'option_d': 'Clear',
                'correct_option': 'B', 'explanation': 'Cloudy means clouds cover the sky.'
            },
            {
                'question': 'Weather with rain falling is called _____?',
                'option_a': 'Sunny', 'option_b': 'Rainy', 'option_c': 'Snowy', 'option_d': 'Windy',
                'correct_option': 'B', 'explanation': 'Rainy means rain is falling.'
            },
            {
                'question': 'Strong wind blowing is called _____?',
                'option_a': 'Calm', 'option_b': 'Windy', 'option_c': 'Sunny', 'option_d': 'Hot',
                'correct_option': 'B', 'explanation': 'Windy means strong winds.'
            },
            {
                'question': 'Weather with snow falling is _____?',
                'option_a': 'Rainy', 'option_b': 'Snowy', 'option_c': 'Sunny', 'option_d': 'Foggy',
                'correct_option': 'B', 'explanation': 'Snowy means snow is falling.'
            },
            {
                'question': 'High temperature weather is called _____?',
                'option_a': 'Cold', 'option_b': 'Hot', 'option_c': 'Windy', 'option_d': 'Rainy',
                'correct_option': 'B', 'explanation': 'Hot means high temperatures.'
            },
            {
                'question': 'Low visibility due to mist is called _____?',
                'option_a': 'Clear', 'option_b': 'Foggy', 'option_c': 'Sunny', 'option_d': 'Windy',
                'correct_option': 'B', 'explanation': 'Foggy means mist reduces visibility.'
            },
            {
                'question': 'Moist air that feels sticky is called _____?',
                'option_a': 'Dry', 'option_b': 'Humid', 'option_c': 'Cold', 'option_d': 'Windy',
                'correct_option': 'B', 'explanation': 'Humid means moist, muggy air.'
            },
            {
                'question': 'What term describes the variety of life in an ecosystem?',
                'option_a': 'Ecosystem', 'option_b': 'Biodiversity', 'option_c': 'Habitat', 'option_d': 'Climate',
                'correct_option': 'B', 'explanation': 'Biodiversity refers to the variety of life forms.', 'is_premium': True
            },
        ]
        for i, mcq in enumerate(mcqs_8_1):
            MCQ.objects.get_or_create(
                mcq_set=mcqs8_1,
                question=mcq['question'],
                defaults={
                    'option_a': mcq['option_a'], 'option_b': mcq['option_b'],
                    'option_c': mcq['option_c'], 'option_d': mcq['option_d'],
                    'correct_option': mcq['correct_option'],
                    'explanation': mcq.get('explanation', ''),
                    'order': i
                }
            )
        self.stdout.write(f'    ✓ Created MCQ Set: {mcqs8_1.name} ({len(mcqs_8_1)} questions)')

        # =============================================================================
        # SET PREMIUM FLAGS ON EXISTING CONTENT (fix get_or_create issue)
        # =============================================================================
        # Set premium topics
        premium_topic_names = ['Business', 'Technology', 'Health & Wellness', 'Sports']
        Topic.objects.filter(name__in=premium_topic_names).update(is_premium=True)
        Topic.objects.exclude(name__in=premium_topic_names).update(is_premium=False)

        # Set premium flashcard sets
        premium_set_names = ['Food Items', 'Food Vocabulary', 'Airport & Flights']
        FlashcardSet.objects.filter(name__in=premium_set_names).update(is_premium=True)

        # Set premium MCQ sets
        premium_mcq_set_names = ['Food Vocabulary', 'Airport Vocabulary']
        MCQSet.objects.filter(name__in=premium_mcq_set_names).update(is_premium=True)

        # Set individual premium items
        Flashcard.objects.filter(front__in=['Sommelier', 'Salutations', 'Biodiversity']).update(is_premium=True)
        MCQ.objects.filter(question__icontains='French term').update(is_premium=True)
        MCQ.objects.filter(question__icontains='Salutations').update(is_premium=True)
        MCQ.objects.filter(question__icontains='Biodiversity').update(is_premium=True)

        # =============================================================================
        # FINAL SUMMARY
        # =============================================================================
        total_users = CustomUser.objects.count()
        total_subscriptions = Subscription.objects.count()
        total_topics = Topic.objects.count()
        total_flashcard_sets = FlashcardSet.objects.count()
        total_flashcards = Flashcard.objects.count()
        total_mcq_sets = MCQSet.objects.count()
        total_mcqs = MCQ.objects.count()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Mock Data Loaded Successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📊 SUMMARY:'))
        self.stdout.write(f'  Users: {total_users}')
        self.stdout.write(f'  Subscriptions: {total_subscriptions}')
        self.stdout.write(f'  Topics: {total_topics}')
        self.stdout.write(f'  Flashcard Sets: {total_flashcard_sets}')
        self.stdout.write(f'  Flashcards: {total_flashcards}')
        self.stdout.write(f'  MCQ Sets: {total_mcq_sets}')
        self.stdout.write(f'  MCQs: {total_mcqs}')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('🔐 TEST CREDENTIALS:'))
        self.stdout.write('  Admin: admin@test.com / Admin123!')
        self.stdout.write('  Creator: creator1@test.com / Creator123!')
        self.stdout.write('  User: user1@test.com / User123!')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📚 CONTENT OVERVIEW:'))
        self.stdout.write('  8 Topics (4 Free, 4 Premium)')
        self.stdout.write('  14 Flashcard Sets (~140 cards, mixed free/premium)')
        self.stdout.write('  10 MCQ Sets (~80 questions, mixed free/premium)')
        self.stdout.write('')
        self.stdout.write('  Premium Content:')
        self.stdout.write('    - Topics: Business, Technology, Health & Wellness, Sports')
        self.stdout.write('    - Some sets and individual items within free topics')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('🌐 API ENDPOINTS:'))
        self.stdout.write('  Topics: GET /api/content/topics/')
        self.stdout.write('  Flashcards: GET /api/content/flashcards/?set_id=X')
        self.stdout.write('  MCQs: GET /api/content/mcqs/?set_id=X')
        self.stdout.write('  Quiz: GET /api/content/mcqs/quiz/<set_id>/')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Login via: POST /api/auth/login/'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Ready to test! Open http://localhost:8000/swagger/'))
        self.stdout.write('')
