from django.contrib import admin
from django.utils.html import format_html
from .models import Question, Tag, KompetensiDasar

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
    list_display = ('short_text', 'question_type', 'difficulty', 'topic_info', 'points', 'created_at')
    list_filter = ('topic__subject', 'topic__subject__grade', 'question_type', 'difficulty', 'created_at')
    search_fields = ('question_text', 'topic__name')
    filter_horizontal = ('tags', 'kompetensi_dasar')
    autocomplete_fields = ['topic']
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Content', {
            'fields': ('topic', 'question_text', 'question_type', 'difficulty', 'points')
        }),
        ('Options & Answer', {
            'fields': ('options', 'answer_key', 'explanation'),
            'classes': ('collapse',),
        }),
        ('Media', {
            'fields': ('image', 'has_math'),
        }),
        ('Metadata', {
            'fields': ('tags', 'kompetensi_dasar', 'estimated_time', 'order')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at')
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def short_text(self, obj):
        return (obj.question_text[:50] + '...') if len(obj.question_text) > 50 else obj.question_text
    short_text.short_description = "Question"

    def topic_info(self, obj):
        return f"{obj.topic.subject.name} - {obj.topic.name}"
    topic_info.short_description = "Topic"
