"""
Management command to fix pilgan answer keys.
Convert free-text answer keys to A, B, C, or D format.
"""
from django.core.management.base import BaseCommand
from apps.questions.models import Question


class Command(BaseCommand):
    help = 'Fix pilgan questions with invalid answer_key format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually changing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all pilgan questions
        pilgan_questions = Question.objects.filter(question_type=Question.Type.PILGAN)
        
        total = pilgan_questions.count()
        fixed = 0
        errors = 0
        
        self.stdout.write(f"\nChecking {total} pilgan questions...")
        
        for question in pilgan_questions:
            answer_key = question.answer_key.strip().upper()
            
            # Check if already valid
            if answer_key in ['A', 'B', 'C', 'D']:
                continue
            
            self.stdout.write(
                self.style.WARNING(
                    f"\n❌ Question ID {question.id}: '{question.question_text[:50]}...'"
                )
            )
            self.stdout.write(f"   Current answer_key: '{question.answer_key}'")
            self.stdout.write(f"   Options: {question.options}")
            
            # Try to intelligently fix
            # This requires manual review - just flag for now
            errors += 1
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS(f"\n✅ Valid questions: {total - errors}"))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"❌ Invalid questions: {errors}"))
            self.stdout.write(
                self.style.WARNING(
                    f"\nPlease manually fix the invalid questions in Django admin."
                )
            )
            self.stdout.write(
                "Kunci jawaban pilihan ganda harus berupa A, B, C, atau D.\n"
            )
        else:
            self.stdout.write(self.style.SUCCESS("✅ All pilgan questions are valid!"))
