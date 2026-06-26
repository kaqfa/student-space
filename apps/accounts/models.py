from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    
    Roles:
    - admin: System administrator with full access
    - parent: Parent/Teacher/Guardian who manages students
    - student: Learner who can take quizzes (can self-register)
    """
    
    class Role(models.TextChoices):
        ADMIN = "admin", _("Administrator")
        PARENT = "parent", _("Parent")  # Changed from pengajar
        STUDENT = "student", _("Student")
        TUTOR = "tutor", _("Tutor")

    role = models.CharField(
        _("Role"), max_length=20, choices=Role.choices, default=Role.STUDENT
    )
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone = models.CharField(_("Phone Number"), max_length=20, blank=True)
    
    # Student-specific fields (nullable for non-students)
    grade = models.IntegerField(
        _("Grade/Kelas"),
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        null=True,
        blank=True,
        help_text=_("Only for students: Grade level (1-6)")
    )
    grade_ref = models.ForeignKey(
        "academic.Grade", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text=_("New grade reference (replaces integer grade)."),
    )
    date_of_birth = models.DateField(
        _("Date of Birth"),
        null=True,
        blank=True,
        help_text=_("Only for students")
    )

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["grade"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # Role check properties
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_parent(self):
        return self.role == self.Role.PARENT

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_tutor(self):
        return self.role == self.Role.TUTOR

    @property
    def family(self):
        """First family this user belongs to (via membership), or None."""
        membership = self.family_memberships.select_related("family").first()
        return membership.family if membership else None

    @property
    def current_enrollment(self):
        """Active enrollment for the active academic year, or None."""
        return (
            self.enrollments
            .filter(status="active", academic_year__is_active=True)
            .select_related("grade", "academic_year")
            .first()
        )

    @property
    def is_parent_or_admin(self):
        """Check if user is parent or admin (for permission checks)"""
        return self.role in [self.Role.ADMIN, self.Role.PARENT] or self.is_superuser

    # Backward compatibility alias
    @property
    def is_pengajar_or_admin(self):
        """Deprecated: Use is_parent_or_admin instead"""
        return self.is_parent_or_admin

    def get_linked_students(self):
        """Get all students linked to this parent (approved only)"""
        if not self.is_parent:
            return User.objects.none()
        return User.objects.filter(
            parent_links__parent=self,
            parent_links__status=ParentStudent.Status.APPROVED,
            role=self.Role.STUDENT
        )

    def get_linked_parents(self):
        """Get all parents linked to this student (approved only)"""
        if not self.is_student:
            return User.objects.none()
        return User.objects.filter(
            student_links__student=self,
            student_links__status=ParentStudent.Status.APPROVED,
            role=self.Role.PARENT
        )


class ParentStudent(models.Model):
    """
    Linking table between Parent and Student with verification workflow.
    
    Flow:
    1. Parent creates new student account -> auto-approved (created_by_parent=True)
    2. Parent links existing student -> pending -> student approves/rejects
    3. Student can work independently without any parent
    """
    
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending Verification")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="student_links",
        limit_choices_to={"role": User.Role.PARENT},
        verbose_name=_("Parent")
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="parent_links",
        limit_choices_to={"role": User.Role.STUDENT},
        verbose_name=_("Student")
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_by_parent = models.BooleanField(
        _("Created by Parent"),
        default=False,
        help_text=_("True if parent created the student account")
    )
    notes = models.TextField(
        _("Notes"),
        blank=True,
        help_text=_("Parent's notes about this student")
    )
    family = models.ForeignKey(
        "accounts.Family", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="parent_student_links",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(
        _("Verified At"),
        null=True,
        blank=True
    )

    class Meta:
        db_table = "parent_students"
        verbose_name = _("Parent-Student Link")
        verbose_name_plural = _("Parent-Student Links")
        unique_together = ["parent", "student"]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["parent", "status"]),
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self):
        return f"{self.parent.get_full_name() or self.parent.username} → {self.student.get_full_name() or self.student.username} ({self.get_status_display()})"

    def approve(self):
        """Approve the link request"""
        self.status = self.Status.APPROVED
        self.verified_at = timezone.now()
        self.save(update_fields=["status", "verified_at"])

    def reject(self):
        """Reject the link request"""
        self.status = self.Status.REJECTED
        self.verified_at = timezone.now()
        self.save(update_fields=["status", "verified_at"])

    @classmethod
    def create_with_new_student(cls, parent, student):
        """Create link when parent creates a new student account"""
        return cls.objects.create(
            parent=parent,
            student=student,
            status=cls.Status.APPROVED,
            created_by_parent=True,
            verified_at=timezone.now()
        )

    @classmethod
    def request_link(cls, parent, student, notes=""):
        """Request to link parent to existing student (requires verification)"""
        return cls.objects.create(
            parent=parent,
            student=student,
            status=cls.Status.PENDING,
            created_by_parent=False,
            notes=notes
        )


class Family(models.Model):
    """Household unit grouping parents, students, and tutors (tenancy root)."""

    name = models.CharField(_("Family Name"), max_length=150)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_families",
        verbose_name=_("Owner"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "families"
        verbose_name = _("Family")
        verbose_name_plural = _("Families")
        ordering = ["name"]

    def __str__(self):
        return self.name


class FamilyMembership(models.Model):
    """Membership linking a User to a Family (M2M through)."""

    class RoleInFamily(models.TextChoices):
        PARENT = "parent", _("Parent")
        STUDENT = "student", _("Student")
        TUTOR = "tutor", _("Tutor")

    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="family_memberships"
    )
    role_in_family = models.CharField(
        _("Role in Family"), max_length=20, choices=RoleInFamily.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "family_memberships"
        verbose_name = _("Family Membership")
        verbose_name_plural = _("Family Memberships")
        unique_together = ["family", "user"]
        ordering = ["family", "role_in_family"]

    def __str__(self):
        return f"{self.user} @ {self.family} ({self.get_role_in_family_display()})"


class ParentProfile(models.Model):
    """Thin profile holding parent preferences."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="parent_profile"
    )
    notification_prefs = models.JSONField(default=dict, blank=True)
    phone = models.CharField(_("Phone (secondary)"), max_length=20, blank=True)

    class Meta:
        db_table = "parent_profiles"
        verbose_name = _("Parent Profile")
        verbose_name_plural = _("Parent Profiles")

    def __str__(self):
        return f"ParentProfile({self.user})"


class TutorProfile(models.Model):
    """Thin profile for tutors."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="tutor_profile"
    )
    bio = models.TextField(blank=True)
    specialization = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = "tutor_profiles"
        verbose_name = _("Tutor Profile")
        verbose_name_plural = _("Tutor Profiles")

    def __str__(self):
        return f"TutorProfile({self.user})"
