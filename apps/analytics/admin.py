from django.contrib import admin
from .models import Attempt

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'question_short', 'is_correct', 'points_earned', 'time_taken', 'created_at')
    list_filter = ('is_correct', 'created_at', 'question__topic__subject')
    search_fields = ('student__username', 'question__question_text')
    readonly_fields = ('student', 'question', 'quiz_session', 'answer_given', 'is_correct', 'points_earned', 'time_taken', 'created_at')
    
    def student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username
    student_name.short_description = "Student"
    
    def question_short(self, obj):
        return (obj.question.question_text[:50] + '...') if len(obj.question.question_text) > 50 else obj.question.question_text
    question_short.short_description = "Question"
