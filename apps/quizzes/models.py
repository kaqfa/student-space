from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.questions.models import Question
from apps.subjects.models import Subject


class Quiz(models.Model):
    """Quiz template created by parent/admin with a set of questions."""
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text=_("Kelas (1-6)")
    )
    
    questions = models.ManyToManyField(Question, related_name='quizzes')
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_quizzes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    time_limit_minutes = models.IntegerField(
        default=30,
        help_text=_("Waktu pengerjaan dalam menit")
    )
    passing_score = models.IntegerField(
        default=70,
        help_text=_("Nilai minimal kelulusan (0-100)")
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizzes")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.title} (Kelas {self.grade})"
    
    @property
    def total_points(self):
        return sum(q.points for q in self.questions.all())
    
    @property
    def question_count(self):
        return self.questions.count()


class QuizSession(models.Model):
    """
    A quiz session represents a student taking a quiz.
    
    Can be:
    - Direct: Student takes quiz from their own account
    - Proxy: Parent runs quiz on behalf of student (e.g., for young children)
    """
    
    # Student who takes the quiz (User with role='student')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_sessions',
        limit_choices_to={'role': 'student'},
        verbose_name=_("Student")
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    # Grade for subject filtering (defaults to student's grade)
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text=_("Kelas untuk filter mata pelajaran")
    )
    
    # Scoring
    score = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Proxy Quiz Mode - Parent runs quiz on behalf of student
    is_proxy_mode = models.BooleanField(
        default=False,
        help_text=_("True jika quiz dijalankan oleh parent atas nama student")
    )
    proxy_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proxy_quiz_sessions',
        limit_choices_to={'role': 'parent'},
        help_text=_("Parent yang menjalankan proxy quiz"),
        verbose_name=_("Proxy User")
    )
    
    class Meta:
        verbose_name = _("Quiz Session")
        verbose_name_plural = _("Quiz Sessions")
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['student', 'completed_at']),
            models.Index(fields=['grade']),
        ]
    
    def __str__(self):
        prefix = "[PROXY] " if self.is_proxy_mode else ""
        student_name = self.student.get_full_name() or self.student.username
        return f"{prefix}{student_name} - {self.quiz.title}"
    
    def save(self, *args, **kwargs):
        # Default grade to student's grade if not set
        if not self.grade and self.student and self.student.grade:
            self.grade = self.student.grade
        super().save(*args, **kwargs)
    
    @property
    def is_completed(self):
        return self.completed_at is not None
    
    @property
    def duration_minutes(self):
        """Return duration in minutes if completed."""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() / 60)
        return None


# Note: Responses/Attempts are stored in apps.analytics.models.Attempt
