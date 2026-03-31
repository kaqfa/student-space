from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.questions.models import Question
from apps.subjects.models import Subject


class Quiz(models.Model):
    """Quiz template created by parent/admin with a set of questions."""
    
    class QuizType(models.TextChoices):
        SUBJECT_BASED = "subject_based", _("Subject Quiz (Random)")
        CUSTOM = "custom", _("Custom Quiz")
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text=_("Kelas (1-6)")
    )
    
    quiz_type = models.CharField(
        max_length=20,
        choices=QuizType.choices,
        default=QuizType.CUSTOM,
        help_text=_("Type of quiz: Subject (random questions) or Custom (specific questions)")
    )
    
    # For custom quizzes: manually selected questions
    # For subject quizzes: this remains empty, questions selected at session creation
    questions = models.ManyToManyField(
        Question, 
        related_name='quizzes',
        blank=True,
        help_text=_("Only for Custom Quiz: manually select questions")
    )
    
    # Number of questions to use in quiz session (random selection)
    # - Subject Quiz: random from all questions in subject
    # - Custom Quiz: random from manually selected questions
    question_count = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_("Number of random questions to use per quiz session")
    )
    
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
        quiz_type_label = "Random" if self.quiz_type == self.QuizType.SUBJECT_BASED else "Custom"
        return f"{self.title} [{quiz_type_label}] (Kelas {self.grade})"
    
    def clean(self):
        """Validate quiz type configuration."""
        from django.core.exceptions import ValidationError
        
        if self.quiz_type == self.QuizType.SUBJECT_BASED:
            # Subject quiz must have question_count but no manual questions
            if not self.question_count:
                raise ValidationError({
                    'question_count': _("Subject Quiz requires a question count.")
                })
            # Only check questions M2M if object is already saved (has pk)
            if self.pk and self.questions.exists():
                raise ValidationError({
                    'questions': _("Subject Quiz should not have manually selected questions.")
                })
        
        elif self.quiz_type == self.QuizType.CUSTOM:
            # Custom quiz must have manual questions selected
            # question_count is optional - if not set, use all selected questions
            if self.pk and not self.questions.exists():
                raise ValidationError({
                    'questions': _("Custom Quiz must have at least one question selected.")
                })
            # If question_count is set, it can't exceed available questions
            if self.pk and self.question_count:
                available = self.questions.count()
                if self.question_count > available:
                    raise ValidationError({
                        'question_count': _(f"Question count ({self.question_count}) cannot exceed available questions ({available}).")
                    })
    
    @property
    def total_points(self):
        """Calculate total points. For subject quiz, this is an estimate."""
        if self.quiz_type == self.QuizType.SUBJECT_BASED:
            # Return estimated total (assuming 10 points per question as default)
            return (self.question_count or 0) * 10
        return sum(q.points for q in self.questions.all())
    
    @property
    def get_question_count(self):
        """Get question count regardless of quiz type."""
        if self.quiz_type == self.QuizType.SUBJECT_BASED:
            return self.question_count or 0
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
    
    # The actual questions used in this session
    # For subject-based quizzes: randomly selected questions
    # For custom quizzes: copied from quiz.questions
    session_questions = models.ManyToManyField(
        Question,
        related_name='quiz_sessions',
        blank=True,
        help_text=_("Questions actually used in this quiz session")
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
        # Check if this is a new session
        is_new = self.pk is None
        
        # Default grade to student's grade if not set
        if not self.grade and self.student and self.student.grade:
            self.grade = self.student.grade
        
        super().save(*args, **kwargs)
        
        # After saving, populate session_questions if not already set
        if is_new and not self.session_questions.exists():
            self._populate_session_questions()
    
    def _populate_session_questions(self):
        """Populate session_questions based on quiz type and pre-generate Attempt records."""
        from random import sample
        
        selected_questions = []
        
        if self.quiz.quiz_type == Quiz.QuizType.SUBJECT_BASED:
            # Subject Quiz: Select random questions from the quiz's subject
            available_questions = list(
                Question.objects.filter(
                    topic__subject=self.quiz.subject,
                    topic__subject__grade=self.quiz.grade
                )
            )
            
            # Get the count, limiting to available questions
            count = min(self.quiz.question_count or 10, len(available_questions))
            
            if available_questions:
                selected_questions = sample(available_questions, count)
        
        elif self.quiz.quiz_type == Quiz.QuizType.CUSTOM:
            # Custom Quiz: Select random from manually selected questions
            available_questions = list(self.quiz.questions.all())
            
            if self.quiz.question_count:
                # If question_count is set, select random subset
                count = min(self.quiz.question_count, len(available_questions))
                selected_questions = sample(available_questions, count)
            else:
                # If no question_count, use all selected questions
                selected_questions = available_questions
        
        # Set the session questions
        if selected_questions:
            self.session_questions.set(selected_questions)
            
            # Pre-generate Attempt records with null answers
            self._generate_attempts()
    
    def _generate_attempts(self):
        """Pre-generate Attempt records for all session questions with null answers."""
        from apps.analytics.models import Attempt
        
        for question in self.session_questions.all():
            Attempt.objects.get_or_create(
                student=self.student,
                question=question,
                quiz_session=self,
                defaults={
                    'answer_given': '',  # Empty answer initially
                    'is_correct': False,
                    'time_taken': 0,
                    'points_earned': 0,
                }
            )
    
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
