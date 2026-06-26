from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from apps.accounts.mixins import StudentRequiredMixin
from .metrics import StudentMetrics

User = get_user_model()

# NOTE: System/admin analytics views (admin dashboard, tag heatmap, KD coverage,
# student history, CSV exports) were removed in U0. Those functions move to
# Django Admin (/admin/) in U1. Only student-facing progress remains here.


class StudentProgressView(StudentRequiredMixin, TemplateView):
    """Detailed progress view for students."""
    template_name = "analytics/progress.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user

        if student and student.role == User.Role.STUDENT:
            metrics = StudentMetrics(student)
            context['student'] = student
            context['total_attempts'] = metrics.get_total_attempts()
            context['accuracy'] = metrics.get_accuracy()
            context['total_points'] = metrics.get_total_points()
            context['quiz_stats'] = metrics.get_quiz_stats()
            context['subject_performance'] = metrics.get_subject_performance()
            context['strengths'] = metrics.get_strengths()
            context['weaknesses'] = metrics.get_weaknesses()
            context['accuracy_trend'] = metrics.get_accuracy_trend()

        return context


class AccuracyTrendAPIView(StudentRequiredMixin, TemplateView):
    """Return accuracy trend data as JSON for charts."""

    def get(self, request, *args, **kwargs):
        student = request.user
        if not student or student.role != User.Role.STUDENT:
            return JsonResponse({'error': 'No student profile'}, status=400)

        days = int(request.GET.get('days', 30))
        metrics = StudentMetrics(student)
        data = metrics.get_accuracy_trend(days=days)

        return JsonResponse({
            'labels': [d['date'] for d in data],
            'values': [d['accuracy'] for d in data],
        })
