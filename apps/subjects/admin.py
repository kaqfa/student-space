from django.contrib import admin
from .models import Subject, Topic

class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'order', 'color_preview', 'topic_count')
    list_filter = ('grade',)
    search_fields = ('name',)
    ordering = ('grade', 'order')
    inlines = [TopicInline]
    
    def topic_count(self, obj):
        return obj.topics.count()
    topic_count.short_description = 'Topics'

    def color_preview(self, obj):
        from django.utils.html import format_html
        return format_html(
            '<span style="background-color: {}; width: 20px; height: 20px; display: inline-block; border-radius: 50%; border: 1px solid #ccc;"></span> {}',
            obj.color,
            obj.color
        )
    color_preview.short_description = 'Color'

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'order', 'question_count')
    list_filter = ('subject__grade', 'subject')
    search_fields = ('name', 'subject__name')
    ordering = ('subject__grade', 'subject__order', 'order')
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'
