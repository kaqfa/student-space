"""
Seed initial data for Ruang Belajar.

Assigns permissions to the three permission groups and seeds academic
reference data (EducationLevel / Grade / AcademicYear). Idempotent —
safe to run multiple times.
"""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


GROUP_PERMS = {
    "content_manager": [
        ("questions", "question"), ("questions", "tag"), ("questions", "kompetensidasar"),
        ("subjects", "subject"), ("subjects", "topic"), ("quizzes", "quiz"),
        ("academic", "educationlevel"), ("academic", "grade"),
        ("academic", "academicyear"), ("academic", "gradesubject"),
    ],
    "user_manager": [
        ("accounts", "user"), ("accounts", "parentstudent"), ("academic", "enrollment"),
        ("accounts", "family"), ("accounts", "familymembership"),
        ("accounts", "parentprofile"), ("accounts", "tutorprofile"),
    ],
    "finance": [],  # populated in B7 (subscriptions)
}
ACTIONS = ("add", "change", "view")


class Command(BaseCommand):
    help = "Seed groups+perms and academic reference data. Idempotent."

    def handle(self, *args, **options):
        self.stdout.write("=== seed_initial_data ===")
        for name, models in GROUP_PERMS.items():
            group, _ = Group.objects.get_or_create(name=name)
            perms = []
            for app_label, model in models:
                for action in ACTIONS:
                    codename = f"{action}_{model}"
                    perm = Permission.objects.filter(
                        codename=codename, content_type__app_label=app_label
                    ).first()
                    if perm:
                        perms.append(perm)
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"  skip missing perm {app_label}.{codename}"))
            group.permissions.set(perms)
            self.stdout.write(f"  group {name}: {len(perms)} perms")

        # Academic reference data
        try:
            from apps.academic.models import EducationLevel, Grade, AcademicYear
            from apps.academic.seed import seed_academic_reference
            summary = seed_academic_reference(EducationLevel, Grade, AcademicYear)
            self.stdout.write(self.style.SUCCESS(f"  academic seed: {summary}"))
        except Exception as e:  # academic not migrated yet
            self.stdout.write(self.style.WARNING(f"  academic seed skipped: {e}"))

        self.stdout.write(self.style.SUCCESS("Done."))
