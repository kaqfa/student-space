from django.db import migrations


def forwards(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    ParentStudent = apps.get_model("accounts", "ParentStudent")
    Family = apps.get_model("accounts", "Family")
    FamilyMembership = apps.get_model("accounts", "FamilyMembership")

    parent_ids = (
        ParentStudent.objects.values_list("parent_id", flat=True).distinct()
    )
    for parent_id in parent_ids:
        parent = User.objects.get(pk=parent_id)
        full = f"{parent.first_name} {parent.last_name}".strip()
        name = full or parent.username
        family, _ = Family.objects.get_or_create(
            owner=parent, defaults={"name": f"Keluarga {name}"}
        )
        FamilyMembership.objects.get_or_create(
            family=family, user=parent,
            defaults={"role_in_family": "parent"},
        )
        links = ParentStudent.objects.filter(parent_id=parent_id)
        for link in links:
            FamilyMembership.objects.get_or_create(
                family=family, user_id=link.student_id,
                defaults={"role_in_family": "student"},
            )
            if link.family_id is None:
                link.family = family
                link.save(update_fields=["family"])


def backwards(apps, schema_editor):
    ParentStudent = apps.get_model("accounts", "ParentStudent")
    Family = apps.get_model("accounts", "Family")
    FamilyMembership = apps.get_model("accounts", "FamilyMembership")

    ParentStudent.objects.filter(family__isnull=False).update(family=None)
    FamilyMembership.objects.all().delete()
    Family.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_alter_user_role_family_parentstudent_family_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
