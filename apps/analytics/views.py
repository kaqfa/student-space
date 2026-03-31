from django.views.generic import TemplateView, ListView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from apps.accounts.mixins import ParentOrAdminMixin, StudentRequiredMixin
from .models import Attempt
from .metrics import StudentMetrics, get_student_dashboard_context

User = get_user_model()


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


class AdminAnalyticsDashboardView(ParentOrAdminMixin, TemplateView):
    """Analytics dashboard for teachers/admins."""
    template_name = "analytics/admin_dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get selected student or default to first
        student_id = self.request.GET.get('student')
        
        # Get all student users
        students = User.objects.filter(
            role=User.Role.STUDENT
        ).order_by('grade', 'first_name')
        context['students'] = students
        
        if student_id:
            student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
        else:
            student = students.first()
        
        if student:
            context['selected_student'] = student
            metrics = StudentMetrics(student)
            context['total_attempts'] = metrics.get_total_attempts()
            context['accuracy'] = metrics.get_accuracy()
            context['total_points'] = metrics.get_total_points()
            context['quiz_stats'] = metrics.get_quiz_stats()
            context['subject_performance'] = metrics.get_subject_performance()
            context['strengths'] = metrics.get_strengths()[:5]
            context['weaknesses'] = metrics.get_weaknesses()[:5]
            context['recent_activity'] = metrics.get_recent_activity(days=30)
        
        return context


class StudentAttemptHistoryView(ParentOrAdminMixin, ListView):
    """View all attempts for a specific student."""
    model = Attempt
    template_name = "analytics/attempt_history.html"
    context_object_name = "attempts"
    paginate_by = 50
    
    def get_queryset(self):
        self.student = get_object_or_404(User, pk=self.kwargs['pk'], role=User.Role.STUDENT)
        return Attempt.objects.filter(
            student=self.student
        ).select_related(
            'question', 'question__topic', 'question__topic__subject', 'quiz_session'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = self.student
        return context


# API Endpoints for Charts
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


class TagAnalyticsView(ParentOrAdminMixin, TemplateView):
    """Tag/Skill heatmap analytics view."""
    template_name = "analytics/tag_heatmap.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        student_id = self.request.GET.get('student')
        students = User.objects.filter(role=User.Role.STUDENT).order_by('grade', 'first_name')
        context['students'] = students
        
        if student_id:
            student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
        else:
            student = students.first()
        
        if student:
            context['selected_student'] = student
            metrics = StudentMetrics(student)
            tag_performance = metrics.get_tag_performance()
            
            # Group by level
            context['strengths'] = [t for t in tag_performance if t['level'] == 'strength']
            context['neutral'] = [t for t in tag_performance if t['level'] == 'neutral']
            context['weaknesses'] = [t for t in tag_performance if t['level'] == 'weakness']
            context['tag_performance'] = tag_performance
        
        return context


class KDCoverageView(ParentOrAdminMixin, TemplateView):
    """Kompetensi Dasar coverage view."""
    template_name = "analytics/kd_coverage.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        student_id = self.request.GET.get('student')
        students = User.objects.filter(role=User.Role.STUDENT).order_by('grade', 'first_name')
        context['students'] = students
        
        if student_id:
            student = get_object_or_404(User, pk=student_id, role=User.Role.STUDENT)
        else:
            student = students.first()
        
        if student:
            context['selected_student'] = student
            metrics = StudentMetrics(student)
            kd_coverage = metrics.get_kd_coverage()
            
            # Group by subject
            from collections import defaultdict
            by_subject = defaultdict(list)
            for kd in kd_coverage:
                by_subject[kd['kd'].subject.name].append(kd)
            
            context['kd_coverage'] = kd_coverage
            context['kd_by_subject'] = dict(by_subject)
            
            # Summary stats
            total_kd = len(kd_coverage)
            mastered = len([k for k in kd_coverage if k['mastery'] == 'mastered'])
            developing = len([k for k in kd_coverage if k['mastery'] == 'developing'])
            not_started = len([k for k in kd_coverage if k['mastery'] == 'not_started'])
            
            context['kd_summary'] = {
                'total': total_kd,
                'mastered': mastered,
                'developing': developing,
                'not_started': not_started,
                'coverage_percent': round((total_kd - not_started) / total_kd * 100, 1) if total_kd > 0 else 0,
            }
        
        return context


from .reports import generate_student_report_csv, generate_class_summary_csv


class ExportStudentReportView(ParentOrAdminMixin, TemplateView):
    """Export student report as CSV."""
    
    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
        return generate_student_report_csv(student)


class ExportClassSummaryView(ParentOrAdminMixin, TemplateView):
    """Export class summary as CSV."""
    
    def get(self, request):
        grade = request.GET.get('grade')
        if grade:
            grade = int(grade)
        return generate_class_summary_csv(grade=grade)
