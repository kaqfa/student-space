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
