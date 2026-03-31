"""
Unit tests for Quiz and QuizSession models with new quiz logic.
"""
import pytest
from django.core.exceptions import ValidationError
from apps.quizzes.models import Quiz, QuizSession
from apps.questions.models import Question
from apps.analytics.models import Attempt


@pytest.mark.django_db
class TestQuizModel:
    """Test Quiz model validation and behavior."""
    
    def test_subject_quiz_requires_question_count(self, subject, admin_user):
        """Subject quiz must have question_count."""
        quiz = Quiz(
            title="Test Subject Quiz",
            subject=subject,
            grade=6,
            quiz_type=Quiz.QuizType.SUBJECT_BASED,
            created_by=admin_user,
            question_count=None  # Missing question_count
        )
        
        with pytest.raises(ValidationError) as exc_info:
            quiz.full_clean()
        
        assert 'question_count' in exc_info.value.message_dict
    
    def test_subject_quiz_cannot_have_manual_questions(self, subject, admin_user, question):
        """Subject quiz should not have manually selected questions."""
        quiz = Quiz.objects.create(
            title="Test Subject Quiz",
            subject=subject,
            grade=6,
            quiz_type=Quiz.QuizType.SUBJECT_BASED,
            question_count=10,
            created_by=admin_user
        )
        quiz.questions.add(question)
        
        with pytest.raises(ValidationError) as exc_info:
            quiz.full_clean()
        
        assert 'questions' in exc_info.value.message_dict
    
    def test_custom_quiz_requires_questions(self, subject, admin_user):
        """Custom quiz must have at least one question selected."""
        quiz = Quiz.objects.create(
            title="Test Custom Quiz",
            subject=subject,
            grade=6,
            quiz_type=Quiz.QuizType.CUSTOM,
            created_by=admin_user
        )
        
        with pytest.raises(ValidationError) as exc_info:
            quiz.full_clean()
        
        assert 'questions' in exc_info.value.message_dict
    
    def test_custom_quiz_question_count_cannot_exceed_available(self, subject, admin_user, question):
        """Custom quiz question_count can't exceed selected questions."""
        quiz = Quiz.objects.create(
            title="Test Custom Quiz",
            subject=subject,
            grade=6,
            quiz_type=Quiz.QuizType.CUSTOM,
            question_count=10,  # More than available
            created_by=admin_user
        )
        quiz.questions.add(question)  # Only 1 question
        
        with pytest.raises(ValidationError) as exc_info:
            quiz.full_clean()
        
        assert 'question_count' in exc_info.value.message_dict
    
    def test_custom_quiz_with_valid_question_count(self, subject, admin_user, multiple_questions):
        """Custom quiz can have question_count less than available."""
        quiz = Quiz.objects.create(
            title="Test Custom Quiz",
            subject=subject,
            grade=6,
            quiz_type=Quiz.QuizType.CUSTOM,
            question_count=3,
            created_by=admin_user
        )
        quiz.questions.set(multiple_questions)  # 5 questions
        
        # Should not raise error
        quiz.full_clean()
        assert quiz.question_count == 3


@pytest.mark.django_db
class TestQuizSessionQuestionSelection:
    """Test QuizSession question selection logic."""
    
    def test_subject_quiz_selects_random_questions(self, subject_quiz, student, multiple_questions):
        """Subject quiz should select random questions from subject."""
        session = QuizSession.objects.create(
            student=student,
            quiz=subject_quiz,
            grade=6
        )
        
        assert session.session_questions.count() == subject_quiz.question_count
        # All selected questions should be from the subject
        for q in session.session_questions.all():
            assert q.topic.subject == subject_quiz.subject
    
    def test_custom_quiz_with_question_count_selects_random_subset(self, custom_quiz_with_count, student):
        """Custom quiz with question_count selects random subset."""
        session = QuizSession.objects.create(
            student=student,
            quiz=custom_quiz_with_count,
            grade=6
        )
        
        assert session.session_questions.count() == custom_quiz_with_count.question_count
        # All selected questions should be from quiz's questions
        for q in session.session_questions.all():
            assert q in custom_quiz_with_count.questions.all()
    
    def test_custom_quiz_without_question_count_uses_all(self, custom_quiz_all_questions, student):
        """Custom quiz without question_count uses all selected questions."""
        session = QuizSession.objects.create(
            student=student,
            quiz=custom_quiz_all_questions,
            grade=6
        )
        
        assert session.session_questions.count() == custom_quiz_all_questions.questions.count()
    
    def test_session_pre_generates_attempts(self, subject_quiz, student):
        """QuizSession should pre-generate Attempt records."""
        session = QuizSession.objects.create(
            student=student,
            quiz=subject_quiz,
            grade=6
        )
        
        # Check that Attempts were created
        attempts = Attempt.objects.filter(quiz_session=session)
        assert attempts.count() == session.session_questions.count()
        
        # All attempts should have empty answers initially
        for attempt in attempts:
            assert attempt.answer_given == ''
            assert attempt.is_correct is False
            assert attempt.time_taken == 0
            assert attempt.points_earned == 0


@pytest.mark.django_db
class TestQuizSessionComplettion:
    """Test quiz completion and answer updating."""
    
    def test_finish_quiz_updates_existing_attempts(self, quiz_session_with_attempts):
        """Finishing quiz should update existing Attempt records."""
        session = quiz_session_with_attempts
        
        # Simulate student answers
        post_data = {}
        for question in session.session_questions.all():
            post_data[f'question_{question.id}'] = question.answer_key  # Correct answer
        
        # Before: all attempts have empty answers
        initial_attempts = Attempt.objects.filter(quiz_session=session)
        assert all(a.answer_given == '' for a in initial_attempts)
        
        # Simulate quiz completion (would be done in view)
        for question in session.session_questions.all():
            answer_key = f"question_{question.id}"
            answer_given = post_data.get(answer_key, "").strip().upper()
            
            attempt = Attempt.objects.get(
                student=session.student,
                question=question,
                quiz_session=session
            )
            attempt.answer_given = answer_given
            attempt.is_correct = (answer_given == question.answer_key)
            attempt.save()
        
        # After: all attempts should have answers
        updated_attempts = Attempt.objects.filter(quiz_session=session)
        assert all(a.answer_given != '' for a in updated_attempts)
        assert all(a.is_correct for a in updated_attempts)  # All correct
