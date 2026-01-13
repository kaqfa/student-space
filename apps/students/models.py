"""
DEPRECATED: This module contains the old Student model.

The Student model has been replaced by using User with role='student' directly.
This file is kept for backward compatibility and migration purposes.

New architecture:
- Student is now a User with role='student'
- Parent-Student relationship is managed via accounts.ParentStudent model
- Grade and date_of_birth are now fields on the User model

For new code, use:
- from apps.accounts.models import User, ParentStudent
- User.objects.filter(role='student') to get all students
"""

import warnings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Student(models.Model):
    """
    DEPRECATED: Use User model with role='student' instead.
    
    This model is kept for backward compatibility during migration.
    It will be removed in a future version.
    
    Migration path:
    1. Create User records for each Student with role='student'
    2. Copy grade, date_of_birth to User fields
    3. Create ParentStudent records for parent relationships
    4. Update foreign keys in other models
    5. Remove this model
    """
    
    name = models.CharField(_("Name"), max_length=100)
    grade = models.IntegerField(
        _("Grade"), validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)
    avatar = models.ImageField(upload_to="students/avatars/", null=True, blank=True)
    
    # Parent is usually the admin/user managing the account
    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="children",
    )
    
    # DEPRECATED: pengajar is now 'parent' role
    pengajar = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="old_students",  # Changed to avoid conflict
        limit_choices_to={"role": "parent"},  # Changed from pengajar
        blank=True,
    )
    
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    # Link to new User model (for migration)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="old_student_profile",
        help_text=_("Link to the new User model (for migration)")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "students"
        verbose_name = _("Student (Deprecated)")
        verbose_name_plural = _("Students (Deprecated)")
        ordering = ["grade", "name"]
        indexes = [
            models.Index(fields=["parent", "is_active"]),
            models.Index(fields=["grade"]),
        ]

    def __str__(self):
        return f"{self.name} (Kelas {self.grade})"
    
    def save(self, *args, **kwargs):
        warnings.warn(
            "Student model is deprecated. Use User with role='student' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().save(*args, **kwargs)


def get_student_user(student):
    """
    Helper function to get User from old Student model.
    Returns the linked user or None.
    """
    if student.user:
        return student.user
    return None


def migrate_student_to_user(student, username=None, password=None):
    """
    Helper function to migrate an old Student to new User model.
    
    Args:
        student: Old Student instance
        username: Optional username (defaults to slugified name)
        password: Optional password (defaults to random)
    
    Returns:
        Tuple of (User, ParentStudent)
    """
    from apps.accounts.models import User, ParentStudent
    from django.utils.text import slugify
    import secrets
    
    if student.user:
        return student.user, None
    
    # Generate username if not provided
    if not username:
        base_username = slugify(student.name)
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
    
    # Generate password if not provided
    if not password:
        password = secrets.token_urlsafe(12)
    
    # Create User
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=student.name.split()[0] if student.name else "",
        last_name=" ".join(student.name.split()[1:]) if student.name else "",
        role=User.Role.STUDENT,
        grade=student.grade,
        date_of_birth=student.date_of_birth,
        is_active=student.is_active,
    )
    
    # Link old student to new user
    student.user = user
    student.save(update_fields=["user"])
    
    # Create ParentStudent link
    parent_student = None
    if student.parent and student.parent.role in [User.Role.ADMIN, User.Role.PARENT]:
        # If parent has admin role, we need to handle differently
        # For now, only create link if parent has parent role
        if student.parent.role == User.Role.PARENT:
            parent_student = ParentStudent.create_with_new_student(
                parent=student.parent,
                student=user
            )
    
    return user, parent_student
