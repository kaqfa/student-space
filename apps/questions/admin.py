import json

from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html

from .forms import QuestionImportForm
from .models import Question, Tag, KompetensiDasar
from .services import import_questions_from_json

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'question_count')
    list_filter = ('category',)
    search_fields = ('name',)
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = "Questions"

@admin.register(KompetensiDasar)
class KDAdmin(admin.ModelAdmin):
    list_display = ('code', 'subject', 'grade', 'short_desc')
    list_filter = ('grade', 'subject')
    search_fields = ('code', 'description')
    ordering = ('grade', 'subject', 'code')
    
    def short_desc(self, obj):
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
    short_desc.short_description = "Description"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_text', 'question_type', 'difficulty', 'subject_display', 'topic_display', 'points', 'created_at')
    list_filter = ('question_type', 'difficulty', 'topic__subject__grade', 'topic__subject', 'has_math', 'has_image', 'created_at')
    search_fields = ('question_text', 'topic__name', 'topic__subject__name', 'answer_key')
    filter_horizontal = ('tags', 'kompetensi_dasar')
    autocomplete_fields = ['topic']
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'question_preview')
    list_per_page = 25
    change_list_template = "admin/questions/question_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "import-json/",
                self.admin_site.admin_view(self.import_json_view),
                name="questions_question_import_json",
            ),
        ]
        return custom + urls

    def import_json_view(self, request):
        if request.method == "POST":
            form = QuestionImportForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    data = json.load(request.FILES["file"])
                except json.JSONDecodeError:
                    messages.error(request, "File is not valid JSON.")
                    return redirect("admin:questions_question_changelist")
                count, errors = import_questions_from_json(data, user=request.user)
                if count:
                    messages.success(request, f"Imported {count} questions.")
                for err in errors[:20]:
                    messages.warning(request, err)
                if not count and not errors:
                    messages.warning(request, "No questions imported.")
                return redirect("admin:questions_question_changelist")
        else:
            form = QuestionImportForm()
        context = {
            **self.admin_site.each_context(request),
            "form": form,
            "title": "Import Questions (JSON)",
            "opts": self.model._meta,
        }
        return render(request, "admin/questions/question_import.html", context)

    fieldsets = (
        ('Content', {
            'fields': ('topic', 'question_text', 'question_type', 'difficulty', 'points')
        }),
        ('Options & Answer', {
            'fields': ('options', 'answer_key', 'explanation'),
        }),
        ('Media', {
            'fields': ('image', 'has_image', 'has_math'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('tags', 'kompetensi_dasar', 'estimated_time', 'order')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at', 'question_preview'),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        # Auto-set has_image based on image field
        obj.has_image = bool(obj.image)
        super().save_model(request, obj, form, change)

    def short_text(self, obj):
        return (obj.question_text[:60] + '...') if len(obj.question_text) > 60 else obj.question_text
    short_text.short_description = "Question"

    def subject_display(self, obj):
        return f"{obj.topic.subject.name} (Kelas {obj.topic.subject.grade})"
    subject_display.short_description = "Subject"
    
    def topic_display(self, obj):
        return obj.topic.name
    topic_display.short_description = "Topic"
    
    def question_preview(self, obj):
        from django.utils.html import format_html
        preview = f"<strong>Question:</strong> {obj.question_text}<br>"
        if obj.options and obj.question_type == 'pilgan':
            preview += "<strong>Options:</strong><br>"
            for opt in obj.options:
                preview += f"- {opt}<br>"
        preview += f"<strong>Answer:</strong> {obj.answer_key}<br>"
        if obj.explanation:
            preview += f"<strong>Explanation:</strong> {obj.explanation}"
        return format_html(preview)
    question_preview.short_description = "Preview"
