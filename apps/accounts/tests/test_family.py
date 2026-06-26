import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from apps.accounts.models import (
    Family, FamilyMembership, ParentProfile, TutorProfile, ParentStudent,
)

pytestmark = pytest.mark.django_db
User = get_user_model()


def _parent(username="p1"):
    return User.objects.create_user(username=username, password="x", role="parent")


def _student(username="s1"):
    return User.objects.create_user(username=username, password="x", role="student")


def test_is_tutor():
    t = User.objects.create_user(username="t1", password="x", role="tutor")
    assert t.is_tutor is True
    assert _parent().is_tutor is False


def test_family_and_membership_creation():
    parent = _parent()
    fam = Family.objects.create(name="Keluarga Test", owner=parent)
    FamilyMembership.objects.create(family=fam, user=parent, role_in_family="parent")
    assert fam.memberships.count() == 1


def test_membership_unique_per_user():
    parent = _parent()
    fam = Family.objects.create(name="Keluarga Test", owner=parent)
    FamilyMembership.objects.create(family=fam, user=parent, role_in_family="parent")
    with pytest.raises(IntegrityError):
        FamilyMembership.objects.create(family=fam, user=parent, role_in_family="tutor")


def test_user_family_helper():
    parent = _parent()
    assert parent.family is None
    fam = Family.objects.create(name="Keluarga Test", owner=parent)
    FamilyMembership.objects.create(family=fam, user=parent, role_in_family="parent")
    assert parent.family == fam


def test_profiles_round_trip():
    parent = _parent()
    tutor = User.objects.create_user(username="t2", password="x", role="tutor")
    pp = ParentProfile.objects.create(user=parent, notification_prefs={"email": True}, phone="0812")
    tp = TutorProfile.objects.create(user=tutor, bio="hi", specialization="Math")
    assert parent.parent_profile == pp
    assert tutor.tutor_profile == tp
    assert pp.notification_prefs["email"] is True


def test_backfill_creates_family_from_links(django_assert_num_queries=None):
    """Simulate the backfill logic: a parent with two students -> one family, 3 memberships."""
    parent = _parent("p_bf")
    s1 = _student("s_bf1")
    s2 = _student("s_bf2")
    ParentStudent.objects.create(parent=parent, student=s1, status="approved")
    ParentStudent.objects.create(parent=parent, student=s2, status="approved")

    # Re-run the same logic the data migration uses.
    fam, _ = Family.objects.get_or_create(owner=parent, defaults={"name": f"Keluarga {parent.username}"})
    FamilyMembership.objects.get_or_create(family=fam, user=parent, defaults={"role_in_family": "parent"})
    for link in ParentStudent.objects.filter(parent=parent):
        FamilyMembership.objects.get_or_create(
            family=fam, user_id=link.student_id, defaults={"role_in_family": "student"}
        )
        link.family = fam
        link.save(update_fields=["family"])

    assert Family.objects.filter(owner=parent).count() == 1
    assert fam.memberships.count() == 3
    assert ParentStudent.objects.filter(parent=parent, family=fam).count() == 2
