from django.db.models import Count, Avg, Sum, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from apps.analytics.models import Attempt
from apps.quizzes.models import QuizSession


class StudentMetrics:
    """Calculate various metrics for a student."""
    
    def __init__(self, student):
        self.student = student
        self._attempts = None
        self._quiz_sessions = None
    
    @property
    def attempts(self):
        if self._attempts is None:
            self._attempts = Attempt.objects.filter(student=self.student)
        return self._attempts
    
    @property
    def quiz_sessions(self):
        if self._quiz_sessions is None:
            self._quiz_sessions = QuizSession.objects.filter(student=self.student)
        return self._quiz_sessions
    
    def get_total_attempts(self):
        """Total number of question attempts."""
        return self.attempts.count()
    
    def get_correct_attempts(self):
        """Number of correct attempts."""
        return self.attempts.filter(is_correct=True).count()
    
    def get_accuracy(self):
        """Overall accuracy percentage."""
        total = self.get_total_attempts()
        if total == 0:
            return 0
        correct = self.get_correct_attempts()
        return round((correct / total) * 100, 1)
    
    def get_total_points(self):
        """Total XP/points earned."""
        return self.attempts.aggregate(total=Sum('points_earned'))['total'] or 0
    
    def get_total_xp(self):
        """Alias for get_total_points."""
        return self.get_total_points()
    
    def get_quiz_stats(self):
        """Quiz completion statistics."""
        completed = self.quiz_sessions.filter(completed_at__isnull=False)
        return {
            'total_taken': completed.count(),
            'passed': completed.filter(passed=True).count(),
            'avg_score': completed.aggregate(avg=Avg('score'))['avg'] or 0,
        }
    
    def get_subject_performance(self):
        """Performance breakdown by subject."""
        from apps.subjects.models import Subject
        
        performance = []
        subjects = Subject.objects.filter(grade=self.student.grade)
        
        for subject in subjects:
            subject_attempts = self.attempts.filter(
                question__topic__subject=subject
            )
            total = subject_attempts.count()
            correct = subject_attempts.filter(is_correct=True).count()
            accuracy = round((correct / total) * 100, 1) if total > 0 else 0
            
            performance.append({
                'subject': subject,
                'total': total,
                'correct': correct,
                'accuracy': accuracy,
            })
        
        return performance
    
    def get_recent_activity(self, days=7):
        """Get recent attempts grouped by date."""
        since = timezone.now() - timedelta(days=days)
        return self.attempts.filter(
            created_at__gte=since
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        ).order_by('-date')[:7]
    
    def get_accuracy_trend(self, days=30):
        """Accuracy over time for charting."""
        since = timezone.now() - timedelta(days=days)
        daily_stats = self.attempts.filter(
            created_at__gte=since
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        ).order_by('date')
        
        result = []
        for stat in daily_stats:
            accuracy = round((stat['correct'] / stat['total']) * 100, 1) if stat['total'] > 0 else 0
            result.append({
                'date': stat['date'].strftime('%Y-%m-%d'),
                'accuracy': accuracy,
                'total': stat['total'],
            })
        return result
    
    def get_strengths(self, min_attempts=3, threshold=80):
        """Topics where student performs well."""
        from apps.subjects.models import Topic
        
        topic_stats = self.attempts.values(
            'question__topic'
        ).annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        ).filter(total__gte=min_attempts)
        
        strengths = []
        for stat in topic_stats:
            accuracy = (stat['correct'] / stat['total']) * 100
            if accuracy >= threshold:
                topic = Topic.objects.get(pk=stat['question__topic'])
                strengths.append({
                    'topic': topic,
                    'accuracy': round(accuracy, 1),
                    'attempts': stat['total'],
                })
        
        return sorted(strengths, key=lambda x: -x['accuracy'])
    
    def get_weaknesses(self, min_attempts=3, threshold=60):
        """Topics where student struggles."""
        from apps.subjects.models import Topic
        
        topic_stats = self.attempts.values(
            'question__topic'
        ).annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        ).filter(total__gte=min_attempts)
        
        weaknesses = []
        for stat in topic_stats:
            accuracy = (stat['correct'] / stat['total']) * 100
            if accuracy < threshold:
                topic = Topic.objects.get(pk=stat['question__topic'])
                weaknesses.append({
                    'topic': topic,
                    'accuracy': round(accuracy, 1),
                    'attempts': stat['total'],
                })
        
        return sorted(weaknesses, key=lambda x: x['accuracy'])
    
    def get_tag_performance(self):
        """Performance breakdown by tag (skill heatmap data)."""
        from apps.questions.models import Tag
        
        tag_stats = self.attempts.filter(
            question__tags__isnull=False
        ).values(
            'question__tags__id',
            'question__tags__name'
        ).annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        ).filter(total__gte=1)
        
        performance = []
        for stat in tag_stats:
            accuracy = round((stat['correct'] / stat['total']) * 100, 1) if stat['total'] > 0 else 0
            # Determine level: strength, neutral, weakness
            if accuracy >= 80:
                level = 'strength'
            elif accuracy >= 60:
                level = 'neutral'
            else:
                level = 'weakness'
            
            performance.append({
                'tag_id': stat['question__tags__id'],
                'tag_name': stat['question__tags__name'],
                'total': stat['total'],
                'correct': stat['correct'],
                'accuracy': accuracy,
                'level': level,
            })
        
        return sorted(performance, key=lambda x: -x['accuracy'])
    
    def get_kd_coverage(self):
        """Kompetensi Dasar coverage and mastery."""
        from apps.questions.models import KompetensiDasar
        
        # Get all KD for student's grade
        all_kd = KompetensiDasar.objects.filter(grade=self.student.grade).select_related('subject')
        
        coverage = []
        for kd in all_kd:
            kd_attempts = self.attempts.filter(
                question__kompetensi_dasar=kd
            )
            total = kd_attempts.count()
            correct = kd_attempts.filter(is_correct=True).count()
            accuracy = round((correct / total) * 100, 1) if total > 0 else 0
            
            # Determine mastery level
            if total == 0:
                mastery = 'not_started'
            elif accuracy >= 80:
                mastery = 'mastered'
            elif accuracy >= 60:
                mastery = 'developing'
            else:
                mastery = 'needs_work'
            
            coverage.append({
                'kd': kd,
                'total': total,
                'correct': correct,
                'accuracy': accuracy,
                'mastery': mastery,
            })
        
        return coverage


def get_student_dashboard_context(student):
    """Helper function to get all dashboard data for a student."""
    metrics = StudentMetrics(student)
    
    return {
        'total_attempts': metrics.get_total_attempts(),
        'accuracy': metrics.get_accuracy(),
        'total_points': metrics.get_total_points(),
        'quiz_stats': metrics.get_quiz_stats(),
        'subject_performance': metrics.get_subject_performance(),
        'recent_activity': metrics.get_recent_activity(),
    }

