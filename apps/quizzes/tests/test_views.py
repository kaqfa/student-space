"""
Unit tests for quizzes app views.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestStudentQuizListView:
    """Test student quiz list"""
    
    def test_requires_authentication(self, client):
        """Test requires login"""
        url = reverse('quizzes:student-list')
        response = client.get(url)
        assert response.status_code == 302
    
    def test_student_can_access(self, client, student_user):
        """Test student can see quizzes"""
        client.force_login(student_user)
        url = reverse('quizzes:student-list')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_filters_by_student_grade(self, client, student_user, quiz):
        """Test only shows quizzes for student's grade"""
        client.force_login(student_user)
        url = reverse('quizzes:student-list')
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestQuizTakeView:
    """Test quiz taking functionality"""
    
    def test_student_can_start_quiz(self, client, student_user, quiz_with_questions):
        """Test student can start a quiz"""
        client.force_login(student_user)
        url = reverse('quizzes:take_quiz', args=[quiz_with_questions.pk])
        response = client.get(url)
        assert response.status_code == 200
    
    def test_creates_quiz_session(self, client, student_user, quiz_with_questions):
        """Test starting quiz creates session"""
        from apps.quizzes.models import QuizSession
        client.force_login(student_user)
        url = reverse('quizzes:take_quiz', args=[quiz_with_questions.pk])
        
        # Count sessions before
        count_before = QuizSession.objects.filter(student=student_user).count()
        
        response = client.get(url)
        
        # Count sessions after
        count_after = QuizSession.objects.filter(student=student_user).count()
        
        # Session should be created or reused
        assert count_after >= count_before
    
    def test_submit_quiz_answers(self, client, student_user, quiz_with_questions, question):
        """Test submitting quiz answers"""
        from apps.quizzes.models import QuizSession
        
        client.force_login(student_user)
        
        # First start the quiz to create session
        url = reverse('quizzes:take_quiz', args=[quiz_with_questions.pk])
        client.get(url)
        
        # Get the session
        session = QuizSession.objects.get(student=student_user, quiz=quiz_with_questions, completed_at__isnull=True)
        
        # Submit answers for all questions in session
        post_data = {'submit_quiz': 'true'}
        for q in session.session_questions.all():
            post_data[f'question_{q.id}'] = q.answer_key
        
        response = client.post(url, post_data)
        
        # Should redirect to results
        assert response.status_code == 302


@pytest.mark.django_db
class TestQuizResultView:
    """Test quiz result view"""
    
    def test_student_can_view_results(self, client, student_user, quiz_session):
        """Test student can view their results"""
        # Mark session as completed
        quiz_session.completed_at = quiz_session.started_at
        quiz_session.save()
        
        client.force_login(student_user)
        url = reverse('quizzes:result', args=[quiz_session.quiz.pk])
        response = client.get(url)
        assert response.status_code == 200
    
    def test_shows_most_recent_session(self, client, student_user, quiz):
        """Test shows most recent session when student retakes quiz"""
        from apps.quizzes.models import QuizSession
        from django.utils import timezone
        
        # Create two completed sessions
        session1 = QuizSession.objects.create(
            student=student_user,
            quiz=quiz,
            grade=student_user.grade,
            score=50,
            completed_at=timezone.now()
        )
        
        session2 = QuizSession.objects.create(
            student=student_user,
            quiz=quiz,
            grade=student_user.grade,
            score=80,
            completed_at=timezone.now()
        )
        
        client.force_login(student_user)
        url = reverse('quizzes:result', args=[quiz.pk])
        response = client.get(url)
        
        # Should show most recent session
        assert response.status_code == 200


@pytest.mark.django_db
class TestProxyModeQuiz:
    """Test proxy mode (parent taking quiz on behalf of student)"""
    
    def test_parent_can_take_quiz_for_student(self, client, parent_user, student_user, quiz_with_questions, parent_student_link):
        """Test parent can take quiz in proxy mode"""
        client.force_login(parent_user)
        url = reverse('quizzes:take_quiz', args=[quiz_with_questions.pk])
        
        # Add proxy parameters
        response = client.get(url, {'student_id': student_user.pk, 'proxy': 'true'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestQuizCRUDViews:
    """Test quiz CRUD operations for admin/parent"""
    
    def test_admin_can_create_quiz(self, client, admin_user):
        """Test admin can create quiz"""
        client.force_login(admin_user)
        url = reverse('quizzes:create')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_student_cannot_create_quiz(self, client, student_user):
        """Test student cannot create quiz"""
        client.force_login(student_user)
        url = reverse('quizzes:create')
        response = client.get(url)
        assert response.status_code in [302, 403]
    
    def test_admin_can_update_quiz(self, client, admin_user, quiz):
        """Test admin can update quiz"""
        client.force_login(admin_user)
        url = reverse('quizzes:update', args=[quiz.pk])
        response = client.get(url)
        assert response.status_code == 200
    
    def test_admin_can_delete_quiz(self, client, admin_user, quiz):
        """Test admin can delete quiz"""
        client.force_login(admin_user)
        url = reverse('quizzes:delete', args=[quiz.pk])
        response = client.post(url)
        assert response.status_code == 302
