from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.questions.models import Question
from apps.quizzes.models import QuizSession


class Attempt(models.Model):
    """
    Records a student's answer to a question.
    
    Tracks:
    - The answer given
    - Whether it was correct
    - Time taken to answer
    - Points earned
    
    Can be linked to a quiz session or standalone (practice mode).
    """
    
    # Student who made the attempt (User with role='student')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attempts",
        limit_choices_to={'role': 'student'},
        verbose_name=_("Student")
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="attempts"
    )
    quiz_session = models.ForeignKey(
        QuizSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attempts",
        verbose_name=_("Quiz Session")
    )
    
    answer_given = models.TextField(_("Answer Given"), blank=True, default='')
    is_correct = models.BooleanField(_("Is Correct"), default=False)
    time_taken = models.IntegerField(
        _("Time Taken"),
        default=0,
        help_text=_("Time taken in seconds")
    )
    points_earned = models.IntegerField(_("Points Earned"), default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attempts"
        verbose_name = _("Attempt")
        verbose_name_plural = _("Attempts")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "created_at"]),
            models.Index(fields=["student", "question"]),
            models.Index(fields=["quiz_session"]),
            models.Index(fields=["is_correct"]),
        ]

    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        student_name = self.student.get_full_name() or self.student.username
        return f"{student_name} - Q{self.question.id} ({status})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate points
        if self.is_correct:
            self.points_earned = self.question.points
        else:
            self.points_earned = 0
        super().save(*args, **kwargs)
