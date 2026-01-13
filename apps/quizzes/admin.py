from django.contrib import admin
from .models import Quiz, QuizSession
from apps.analytics.models import Attempt

class AttemptInline(admin.TabularInline):
    model = Attempt
    extra = 0
    readonly_fields = ('question', 'answer_given', 'is_correct', 'points_earned', 'time_taken')
    can_delete = False
    
    def has_add_permission(self, request, obj):
        return False

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'grade', 'question_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'grade', 'subject')
    search_fields = ('title', 'description')
    filter_horizontal = ('questions',)
    autocomplete_fields = ['subject']
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = "Questions"

@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'quiz_title', 'score', 'passed', 'status_badge', 'started_at', 'duration')
    list_filter = ('passed', 'is_proxy_mode', 'quiz__grade', 'started_at')
    search_fields = ('student__username', 'student__first_name', 'quiz__title')
    readonly_fields = ('student', 'quiz', 'score', 'passed', 'started_at', 'completed_at', 'is_proxy_mode', 'proxy_user')
    inlines = [AttemptInline]
    
    def student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username
    student_name.short_description = "Student"
    
    def quiz_title(self, obj):
        return obj.quiz.title
    quiz_title.short_description = "Quiz"
    
    def status_badge(self, obj):
        from django.utils.html import format_html
        if obj.completed_at:
            color = "green" if obj.passed else "red"
            text = "PASSED" if obj.passed else "FAILED"
        else:
            color = "orange"
            text = "IN PROGRESS"
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 10px;">{}</span>',
            color, text
        )
    status_badge.short_description = "Status"
    
    def duration(self, obj):
        if obj.duration_minutes is not None:
            return f"{obj.duration_minutes} mins"
        return "-"
    duration.short_description = "Duration"
