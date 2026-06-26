from django.conf import settings
from django.db import models


class EducationLevel(models.Model):
    code = models.CharField(max_length=10, unique=True)  # "SD", "SMP"
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Grade(models.Model):
    level = models.ForeignKey(EducationLevel, on_delete=models.CASCADE, related_name="grades")
    number = models.IntegerField()  # 1-9
    label = models.CharField(max_length=50)  # "Kelas 1"
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "number"]
        constraints = [
            models.UniqueConstraint(fields=["level", "number"], name="uniq_grade_level_number"),
        ]

    def __str__(self):
        return self.label


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)  # "2025/2026"
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            AcademicYear.objects.exclude(pk=self.pk).filter(is_active=True).update(is_active=False)


class GradeSubject(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="grade_subjects")
    subject = models.ForeignKey("subjects.Subject", on_delete=models.CASCADE, related_name="grade_subjects")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["grade", "subject"], name="uniq_grade_subject"),
        ]

    def __str__(self):
        return f"{self.grade} - {self.subject}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, related_name="enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-academic_year__name"]
        constraints = [
            models.UniqueConstraint(fields=["student", "academic_year"], name="uniq_enrollment_student_year"),
        ]

    def __str__(self):
        return f"{self.student} @ {self.grade} ({self.academic_year})"
