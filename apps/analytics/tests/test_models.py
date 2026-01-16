"""
Unit tests for analytics app models.
"""
import pytest

from apps.analytics.models import Attempt


@pytest.mark.django_db
class TestAttemptModel:
    """Test Attempt model functionality"""
    
    def test_create_attempt(self, student_user, question, quiz_session):
        """Test creating an attempt"""
        attempt = Attempt.objects.create(
            student=student_user,
            question=question,
            quiz_session=quiz_session,
            answer_given='B',
            is_correct=True,
            time_taken=45
        )
        
        assert attempt.student == student_user
        assert attempt.question == question
        assert attempt.quiz_session == quiz_session
        assert attempt.answer_given == 'B'
        assert attempt.is_correct is True
        assert attempt.time_taken == 45
    
    def test_auto_calculate_points_correct(self, student_user, question, quiz_session):
        """Test that points are auto-calculated for correct answer"""
        attempt = Attempt.objects.create(
            student=student_user,
            question=question,
            quiz_session=quiz_session,
            answer_given='B',
            is_correct=True,
            time_taken=30
        )
        
        # Points should equal question.points (10)
        assert attempt.points_earned == question.points
        assert attempt.points_earned == 10
    
    def test_auto_calculate_points_incorrect(self, student_user, question, quiz_session):
        """Test that points are 0 for incorrect answer"""
        attempt = Attempt.objects.create(
            student=student_user,
            question=question,
            quiz_session=quiz_session,
            answer_given='A',
            is_correct=False,
            time_taken=30
        )
        
        assert attempt.points_earned == 0
    
    def test_attempt_without_quiz_session(self, student_user, question):
        """Test creating attempt without quiz session (practice mode)"""
        attempt = Attempt.objects.create(
            student=student_user,
            question=question,
            answer_given='B',
            is_correct=True,
            time_taken=30
        )
        
        assert attempt.quiz_session is None
        assert attempt.points_earned == question.points
    
    def test_attempt_str_representation(self, student_user, question, quiz_session):
        """Test __str__ method"""
        attempt = Attempt.objects.create(
            student=student_user,
            question=question,
            quiz_session=quiz_session,
            answer_given='B',
            is_correct=True,
            time_taken=30
        )
        
        str_repr = str(attempt)
        assert '✓' in str_repr  # Correct answer symbol
        assert 'Student' in str_repr or 'test_student' in str_repr
    
    def test_attempt_str_incorrect(self, student_user, question, quiz_session):
        """Test __str__ for incorrect answer"""
        attempt = Attempt.objects.create(
            student=student_user,
            question=question,
            quiz_session=quiz_session,
            answer_given='A',
            is_correct=False,
            time_taken=30
        )
        
        str_repr = str(attempt)
        assert '✗' in str_repr  # Incorrect answer symbol
