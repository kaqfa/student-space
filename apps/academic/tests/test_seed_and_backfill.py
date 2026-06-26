import pytest
from apps.academic.models import EducationLevel, Grade, AcademicYear
from apps.academic.seed import seed_academic_reference

pytestmark = pytest.mark.django_db


def _seed():
    return seed_academic_reference(EducationLevel, Grade, AcademicYear)


def test_seed_creates_levels_and_grades():
    _seed()
    sd = EducationLevel.objects.get(code="SD")
    smp = EducationLevel.objects.get(code="SMP")
    assert sorted(sd.grades.values_list("number", flat=True)) == [1, 2, 3, 4, 5, 6]
    assert sorted(smp.grades.values_list("number", flat=True)) == [7, 8, 9]


def test_seed_has_single_active_year():
    _seed()
    assert AcademicYear.objects.filter(is_active=True).count() == 1


def test_seed_is_idempotent():
    _seed()
    _seed()
    assert Grade.objects.count() == 9
    assert EducationLevel.objects.count() == 2
    assert AcademicYear.objects.count() == 1


def test_only_one_active_year_enforced():
    _seed()
    AcademicYear.objects.create(name="2026/2027", is_active=True)
    assert AcademicYear.objects.filter(is_active=True).count() == 1
