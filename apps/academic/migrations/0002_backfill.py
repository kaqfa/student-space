from django.db import migrations


def forwards(apps, schema_editor):
    from apps.academic.seed import seed_academic_reference

    EducationLevel = apps.get_model("academic", "EducationLevel")
    Grade = apps.get_model("academic", "Grade")
    AcademicYear = apps.get_model("academic", "AcademicYear")
    Enrollment = apps.get_model("academic", "Enrollment")
    User = apps.get_model("accounts", "User")
    Subject = apps.get_model("subjects", "Subject")
    KompetensiDasar = apps.get_model("questions", "KompetensiDasar")
    Quiz = apps.get_model("quizzes", "Quiz")
    QuizSession = apps.get_model("quizzes", "QuizSession")

    seed_academic_reference(EducationLevel, Grade, AcademicYear)

    grade_by_number = {g.number: g for g in Grade.objects.all()}
    active_year = AcademicYear.objects.filter(is_active=True).first()

    def backfill(model):
        for obj in model.objects.filter(grade__isnull=False, grade_ref__isnull=True):
            g = grade_by_number.get(obj.grade)
            if g:
                obj.grade_ref = g
                obj.save(update_fields=["grade_ref"])

    for m in (User, Subject, KompetensiDasar, Quiz, QuizSession):
        backfill(m)

    # Enrollment from students' grade
    if active_year:
        for u in User.objects.filter(role="student", grade__isnull=False):
            g = grade_by_number.get(u.grade)
            if not g:
                continue
            Enrollment.objects.get_or_create(
                student=u, academic_year=active_year,
                defaults={"grade": g, "status": "active"},
            )


def backwards(apps, schema_editor):
    Enrollment = apps.get_model("academic", "Enrollment")
    Grade = apps.get_model("academic", "Grade")
    AcademicYear = apps.get_model("academic", "AcademicYear")
    EducationLevel = apps.get_model("academic", "EducationLevel")

    Enrollment.objects.all().delete()
    for model in ("accounts.User", "subjects.Subject", "questions.KompetensiDasar",
                  "quizzes.Quiz", "quizzes.QuizSession"):
        app_label, name = model.split(".")
        M = apps.get_model(app_label, name)
        M.objects.filter(grade_ref__isnull=False).update(grade_ref=None)
    Grade.objects.all().delete()
    AcademicYear.objects.all().delete()
    EducationLevel.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("academic", "0001_initial"),
        ("accounts", "0003_user_grade_ref"),
        ("subjects", "0002_subject_grade_ref"),
        ("questions", "0002_kompetensidasar_grade_ref_kompetensidasar_topic"),
        ("quizzes", "0007_quiz_grade_ref_quizsession_grade_ref"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
