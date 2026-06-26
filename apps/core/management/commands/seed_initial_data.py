"""
Seed initial data for Ruang Belajar.

Phase B0 stub: creates Django groups only.
Academic seed data (EducationLevel, Grade, AcademicYear) pending B1 phase
when the `academic` app models are available.
"""
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


GROUPS = [
    'content_manager',
    'user_manager',
    'finance',
]


class Command(BaseCommand):
    help = 'Seed initial data (groups, education levels, grades). Safe to run multiple times.'

    def handle(self, *args, **options):
        self.stdout.write('=== seed_initial_data ===')

        # --- Django Groups ---
        self.stdout.write('Creating default groups...')
        for name in GROUPS:
            group, created = Group.objects.get_or_create(name=name)
            status = 'created' if created else 'already exists'
            self.stdout.write(f'  [{status}] group: {name}')

        # --- Academic seed data (B1 phase) ---
        # TODO B1: seed EducationLevel (SD, SMP)
        # TODO B1: seed Grade (1-9)
        # TODO B1: seed default AcademicYear
        self.stdout.write(
            self.style.WARNING(
                'Academic seed data pending B1 phase '
                '(EducationLevel / Grade / AcademicYear not yet available).'
            )
        )

        self.stdout.write(self.style.SUCCESS('Done.'))
