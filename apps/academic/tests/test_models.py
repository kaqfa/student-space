import pytest
from django.contrib.auth import get_user_model
from apps.academic.models import EducationLevel, Grade, AcademicYear, Enrollment
from apps.academic.seed import seed_academic_reference

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_current_enrollment_returns_active():
    seed_academic_reference(EducationLevel, Grade, AcademicYear)
    year = AcademicYear.objects.get(is_active=True)
    grade = Grade.objects.get(number=3)
    student = User.objects.create_user(username="s1", password="x", role="student", grade=3)
    Enrollment.objects.create(student=student, grade=grade, academic_year=year, status="active")
    enr = student.current_enrollment
    assert enr is not None
    assert enr.grade.number == 3


def test_current_enrollment_none_when_no_enrollment():
    student = User.objects.create_user(username="s2", password="x", role="student")
    assert student.current_enrollment is None
