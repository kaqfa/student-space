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
    list_display = ('title', 'quiz_type_badge', 'subject', 'grade', 'question_count_display', 'time_limit_minutes', 'is_active', 'created_at')
    list_filter = ('is_active', 'quiz_type', 'grade', 'subject', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('questions',)
    autocomplete_fields = ['subject']
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'total_points')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'quiz_type', 'subject', 'grade', 'is_active')
        }),
        ('Quiz Configuration', {
            'fields': ('time_limit_minutes', 'passing_score', 'question_count', 'questions'),
            'description': 'For Subject Quiz: set question_count. For Custom Quiz: select specific questions.'
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'total_points'),
            'classes': ('collapse',)
        })
    )
    
    change_list_template = 'admin/quizzes/quiz_changelist.html'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def quiz_type_badge(self, obj):
        from django.utils.html import format_html
        colors = {
            'subject_based': '#10b981',  # green
            'custom': '#3b82f6'  # blue
        }
        color = colors.get(obj.quiz_type, '#6b7280')
        label = obj.get_quiz_type_display()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">{}</span>',
            color, label
        )
    quiz_type_badge.short_description = "Type"
    
    def question_count_display(self, obj):
        if obj.quiz_type == 'subject_based':
            return f"{obj.question_count} (random)"
        return obj.questions.count()
    question_count_display.short_description = "Questions"

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
