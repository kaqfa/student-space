from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from apps.subjects.models import Subject, Topic


class KompetensiDasar(models.Model):
    code = models.CharField(max_length=20)  # e.g., "3.1", "4.2"
    description = models.TextField()
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="kompetensi"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kompetensi_dasar"
        verbose_name = _("Kompetensi Dasar")
        verbose_name_plural = _("Kompetensi Dasar")
        ordering = ["grade", "subject", "code"]
        unique_together = ["code", "subject", "grade"]
        indexes = [
            models.Index(fields=["grade", "subject"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.description[:50]}"


class Tag(models.Model):
    class Category(models.TextChoices):
        SKILL = "skill", _("Skill")
        TOPIC = "topic", _("Topic")
        DIFFICULTY = "difficulty", _("Difficulty")
        CUSTOM = "custom", _("Custom")

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.CUSTOM
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tags"
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name


class Question(models.Model):
    class Type(models.TextChoices):
        PILGAN = "pilgan", _("Pilihan Ganda")
        ESSAY = "essay", _("Essay")
        ISIAN = "isian", _("Isian")

    class Difficulty(models.TextChoices):
        MUDAH = "mudah", _("Mudah")
        SEDANG = "sedang", _("Sedang")
        SULIT = "sulit", _("Sulit")

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField(_("Question Text"))
    question_type = models.CharField(max_length=20, choices=Type.choices)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices)
    
    # For pilgan: list of strings ["Option A", "Option B", ...]
    options = models.JSONField(null=True, blank=True)
    
    answer_key = models.TextField(_("Answer Key"))
    explanation = models.TextField(_("Explanation"), blank=True)
    
    # Media & formatting
    has_image = models.BooleanField(default=False)
    image = models.ImageField(upload_to="questions/images/", null=True, blank=True)
    has_math = models.BooleanField(default=False)
    
    # Metadata
    estimated_time = models.IntegerField(default=60, help_text=_("In seconds"))
    points = models.IntegerField(default=10)
    order = models.IntegerField(default=0)
    
    # Relations
    tags = models.ManyToManyField(Tag, related_name="questions", blank=True)
    kompetensi_dasar = models.ManyToManyField(
        KompetensiDasar, related_name="questions", blank=True
    )
    
    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_questions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "questions"
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ["topic", "order"]
        indexes = [
            models.Index(fields=["topic", "difficulty"]),
            models.Index(fields=["question_type"]),
            models.Index(fields=["created_at"]),
        ]

    def clean(self):
        """Validate question data."""
        
        # Validate pilgan answer_key is A, B, C, or D
        if self.question_type == self.Type.PILGAN:
            if not self.answer_key or self.answer_key.upper() not in ['A', 'B', 'C', 'D']:
                raise ValidationError({
                    'answer_key': _('Untuk soal pilihan ganda, kunci jawaban harus A, B, C, atau D.')
                })
            # Ensure answer_key is uppercase
            self.answer_key = self.answer_key.upper()
            
            # Validate options exist
            if not self.options or len(self.options) < 2:
                raise ValidationError({
                    'options': _('Soal pilihan ganda harus memiliki minimal 2 pilihan jawaban.')
                })

    def save(self, *args, **kwargs):
        # Run validation before save
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.topic.name} - {self.question_text[:50]}"
    
    def get_subject(self):
        return self.topic.subject
