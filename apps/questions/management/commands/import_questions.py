from django.core.management.base import BaseCommand, CommandError
import json
import os
from apps.questions.services import import_questions_from_json
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Import questions from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file')
        parser.add_argument('--username', type=str, help='Username to assign as creator (optional)')

    def handle(self, *args, **options):
        file_path = options['file_path']
        username = options.get('username')
        
        if not os.path.exists(file_path):
            raise CommandError(f'File "{file_path}" does not exist')

        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist')
        else:
            # Fallback to first superuser
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                 self.stdout.write(self.style.WARNING("No user assigned (no superuser found)."))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.stdout.write(f"Importing questions from {file_path}...")
            count, errors = import_questions_from_json(data, user=user)

            if count > 0:
                self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} questions."))
            
            if errors:
                self.stdout.write(self.style.WARNING(f"Encountered {len(errors)} errors:"))
                for err in errors:
                    self.stdout.write(self.style.ERROR(f"- {err}"))
            
            if count == 0 and not errors:
                 self.stdout.write(self.style.WARNING("No questions imported."))

        except json.JSONDecodeError:
            raise CommandError(f'File "{file_path}" is not valid JSON')
        except Exception as e:
            raise CommandError(f'Error importing: {str(e)}')
