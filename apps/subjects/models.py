from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    grade = models.IntegerField(
        _("Grade"), validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    order = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, blank=True, help_text="Heroicons name")
    color = models.CharField(max_length=7, default="#3B82F6", help_text="Hex color")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subjects"
        verbose_name = _("Subject")
        verbose_name_plural = _("Subjects")
        ordering = ["grade", "order", "name"]
        unique_together = ["name", "grade"]
        indexes = [
            models.Index(fields=["grade", "order"]),
        ]

    def __str__(self):
        return f"{self.name} (Kelas {self.grade})"


class Topic(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="topics"
    )
    name = models.CharField(_("Topic Name"), max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "topics"
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        ordering = ["subject", "order", "name"]
        indexes = [
            models.Index(fields=["subject", "order"]),
        ]

    def __str__(self):
        return f"{self.subject.name} - {self.name}"
