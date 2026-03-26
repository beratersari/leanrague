"""
Management command to create mock CreatorFields for testing.
Usage: python manage.py create_creator_fields

Creates:
- CreatorFields for existing content creators
- Associates some FlashcardSets and MCQSets to fields
- Creates some purchases for regular users
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from app.models.models import (
    CustomUser,
    UserRole,
    CreatorField,
    CreatorFieldPurchase,
    FlashcardSet,
    MCQSet,
)


class Command(BaseCommand):
    help = 'Create mock CreatorFields for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating mock CreatorFields...'))

        # Get content creators
        creators = list(CustomUser.objects.filter(role=UserRole.CONTENT_CREATOR))
        if not creators:
            self.stdout.write(self.style.ERROR('No content creators found. Run load_mock_data first.'))
            return

        # Get regular users
        users = list(CustomUser.objects.filter(role=UserRole.USER))
        if not users:
            self.stdout.write(self.style.ERROR('No regular users found. Run load_mock_data first.'))
            return

        # Get some flashcard sets and MCQ sets (not already in a creator_field)
        available_fc_sets = list(FlashcardSet.objects.filter(creator_field__isnull=True, is_active=True))
        available_mcq_sets = list(MCQSet.objects.filter(creator_field__isnull=True, is_active=True))

        if not available_fc_sets and not available_mcq_sets:
            self.stdout.write(self.style.WARNING('All sets already in fields. Creating new ones...'))

        total_fields = 0
        total_purchases = 0

        # Create fields for each creator
        for creator in creators:
            # Each creator gets 1-2 fields
            num_fields = 1 if len(creators) >= 2 else 2

            for i in range(num_fields):
                field_name = f"{creator.first_name or creator.email.split('@')[0]}'s {'Italian' if i == 0 else 'Spanish'} Essentials"
                field_desc = f"Learn the basics of {'Italian' if i == 0 else 'Spanish'} with curated flashcard and quiz sets by {creator.full_name}."

                # Check if this field already exists
                existing = CreatorField.objects.filter(creator=creator, name=field_name).first()
                if existing:
                    self.stdout.write(f'  Field "{field_name}" already exists, skipping.')
                    continue

                field = CreatorField.objects.create(
                    creator=creator,
                    name=field_name,
                    description=field_desc,
                    price=Decimal('9.99') if i == 0 else Decimal('14.99'),
                    is_active=True,
                )
                total_fields += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created field: {field.name} by {creator.email} (${field.price})'))

                # Associate some flashcard sets (up to 3)
                fc_sets_to_add = [s for s in available_fc_sets if s.creator_field is None][:3]
                for fs in fc_sets_to_add:
                    fs.creator_field = field
                    fs.save()
                    available_fc_sets.remove(fs)
                    self.stdout.write(f'    → Added flashcard set: {fs.name}')

                # Associate some MCQ sets (up to 2)
                mcq_sets_to_add = [s for s in available_mcq_sets if s.creator_field is None][:2]
                for ms in mcq_sets_to_add:
                    ms.creator_field = field
                    ms.save()
                    available_mcq_sets.remove(ms)
                    self.stdout.write(f'    → Added MCQ set: {ms.name}')

        # Create some purchases
        fields = list(CreatorField.objects.filter(is_active=True))
        for user in users[:3]:  # First 3 users purchase some fields
            for field in fields[:1]:  # Purchase first available field
                if field.creator == user:
                    continue  # Can't purchase own field
                purchase, created = CreatorFieldPurchase.objects.get_or_create(
                    user=user,
                    creator_field=field,
                    defaults={'amount_paid': field.price},
                )
                if created:
                    total_purchases += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ User {user.email} purchased "{field.name}"'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total fields created: {total_fields}'))
        self.stdout.write(self.style.SUCCESS(f'Total purchases created: {total_purchases}'))
        self.stdout.write(self.style.SUCCESS('Done!'))
