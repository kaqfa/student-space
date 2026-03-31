"""
Additional fixtures for E2E tests.
"""
import pytest
from django.utils import timezone
from apps.quizzes.models import QuizSession
from apps.analytics.models import Attempt


@pytest.fixture
def completed_quiz_session(subject_quiz, student):
    """Create a completed quiz session for testing results."""
    session = QuizSession.objects.create(
        student=student,
        quiz=subject_quiz,
        grade=6,
        score=80.0,
        passed=True,
        completed_at=timezone.now()
    )
    
    # Add some attempt records
    for question in session.session_questions.all():
        Attempt.objects.create(
            student=student,
            question=question,
            quiz_session=session,
            answer_given=question.answer_key,
            is_correct=True,
            time_taken=30
        )
    
    return session
