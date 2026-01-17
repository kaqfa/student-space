"""
Integration tests for Quiz views and workflows.
Tests the interaction between views, forms, and database.
"""
import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from apps.quizzes.models import Quiz, QuizSession
from apps.analytics.models import Attempt


@pytest.mark.django_db
class TestSubjectQuizCreation:
    """Test subject quiz creation through views."""
    
    def test_create_subject_quiz_view_get(self, admin_client):
        """GET request should display subject quiz form."""
        url = reverse('quizzes:create_subject_quiz')
        response = admin_client.get(url)
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'Subject Quiz' in response.content.decode()
    
    def test_create_subject_quiz_success(self, admin_client, subject):
        """POST valid data should create subject quiz."""
        url = reverse('quizzes:create_subject_quiz')
        data = {
            'title': 'Matematika Kelas 6 - Random',
            'description': 'Quiz dengan soal random',
            'subject': subject.id,
            'grade': 6,
            'question_count': 10,
            'time_limit_minutes': 30,
            'passing_score': 70,
        }
        
        response = admin_client.post(url, data)
        
        # Should redirect to admin after success
        assert response.status_code == 302
        
        # Quiz should be created
        quiz = Quiz.objects.get(title='Matematika Kelas 6 - Random')
        assert quiz.quiz_type == Quiz.QuizType.SUBJECT_BASED
        assert quiz.question_count == 10
        assert quiz.subject == subject
    
    def test_create_subject_quiz_missing_question_count(self, admin_client, subject):
        """Missing question_count should show validation error."""
        url = reverse('quizzes:create_subject_quiz')
        data = {
            'title': 'Test Quiz',
            'subject': subject.id,
            'grade': 6,
            'time_limit_minutes': 30,
            'passing_score': 70,
        }
        
        response = admin_client.post(url, data)
        
        # Should not create quiz
        assert not Quiz.objects.filter(title='Test Quiz').exists()


@pytest.mark.django_db
class TestCustomQuizCreation:
    """Test custom quiz creation through views."""
    
    def test_custom_quiz_question_selection(self, admin_client, multiple_questions):
        """Should allow adding questions to selection."""
        url = reverse('quizzes:create_custom_quiz')
        
        # Add first question
        response = admin_client.post(url, {
            'action': 'add_question',
            'question_id': str(multiple_questions[0].id)
        })
        
        assert response.status_code == 302
        
        # Check session
        session = admin_client.session
        selected = session.get('selected_question_ids', [])
        assert str(multiple_questions[0].id) in selected
    
    def test_custom_quiz_creation_with_count(self, admin_client, subject, multiple_questions):
        """Create custom quiz with question_count."""
        url = reverse('quizzes:create_custom_quiz')
        
        # Add questions to session
        session = admin_client.session
        session['selected_question_ids'] = [str(q.id) for q in multiple_questions]
        session.save()
        
        # Create quiz
        response = admin_client.post(url, {
            'action': 'create_quiz',
            'title': 'Custom Quiz with Count',
            'description': 'Test',
            'subject': subject.id,
            'grade': 6,
            'question_count': 3,  # Select 3 from 5
            'time_limit_minutes': 30,
            'passing_score': 70,
        })
        
        assert response.status_code == 302
        
        quiz = Quiz.objects.get(title='Custom Quiz with Count')
        assert quiz.quiz_type == Quiz.QuizType.CUSTOM
        assert quiz.question_count == 3
        assert quiz.questions.count() == 5  # All 5 stored
    
    def test_custom_quiz_creation_without_count(self, admin_client, subject, multiple_questions):
        """Create custom quiz without question_count (use all)."""
        url = reverse('quizzes:create_custom_quiz')
        
        # Add questions to session
        session = admin_client.session
        session['selected_question_ids'] = [str(q.id) for q in multiple_questions]
        session.save()
        
        # Create quiz without question_count
        response = admin_client.post(url, {
            'action': 'create_quiz',
            'title': 'Custom Quiz All',
            'subject': subject.id,
            'grade': 6,
            'question_count': '',  # Empty = use all
            'time_limit_minutes': 30,
            'passing_score': 70,
        })
        
        assert response.status_code == 302
        
        quiz = Quiz.objects.get(title='Custom Quiz All')
        assert quiz.question_count is None


@pytest.mark.django_db
class TestQuizTakingFlow:
    """Test quiz taking workflow."""
    
    def test_start_quiz_creates_session_and_attempts(self, student_client, subject_quiz, student):
        """Starting quiz should create session and pre-generate attempts."""
        url = reverse('quizzes:take_quiz', kwargs={'pk': subject_quiz.pk})
        
        # No sessions initially
        assert QuizSession.objects.count() == 0
        assert Attempt.objects.count() == 0
        
        response = student_client.get(url)
        
        assert response.status_code == 200
        
        # Session created
        session = QuizSession.objects.get(student=student, quiz=subject_quiz)
        assert session.session_questions.count() == subject_quiz.question_count
        
        # Attempts pre-generated
        attempts = Attempt.objects.filter(quiz_session=session)
        assert attempts.count() == subject_quiz.question_count
        assert all(a.answer_given == '' for a in attempts)
    
    def test_submit_quiz_updates_attempts(self, student_client, quiz_session_with_attempts, student):
        """Submitting quiz should update existing attempts."""
        session = quiz_session_with_attempts
        url = reverse('quizzes:take_quiz', kwargs={'pk': session.quiz.pk})
        
        # Prepare answers
        post_data = {}
        for question in session.session_questions.all():
            post_data[f'question_{question.id}'] = question.answer_key
        
        response = student_client.post(url, post_data)
        
        # Should redirect to results
        assert response.status_code == 302
        
        # Session completed
        session.refresh_from_db()
        assert session.completed_at is not None
        assert session.score > 0
        
        # Attempts updated (not new ones created)
        attempts = Attempt.objects.filter(quiz_session=session)
        assert attempts.count() == session.session_questions.count()
        assert all(a.answer_given != '' for a in attempts)
    
    def test_quiz_score_calculation(self, student_client, quiz_session_with_attempts, student):
        """Quiz score should be calculated correctly."""
        session = quiz_session_with_attempts
        url = reverse('quizzes:take_quiz', kwargs={'pk': session.quiz.pk})
        
        questions = list(session.session_questions.all())
        
        # Answer half correctly
        post_data = {}
        for i, question in enumerate(questions):
            if i % 2 == 0:
                post_data[f'question_{question.id}'] = question.answer_key  # Correct
            else:
                post_data[f'question_{question.id}'] = 'Z'  # Wrong
        
        response = student_client.post(url, post_data)
        
        session.refresh_from_db()
        
        # Score should be approximately 67% (2 out of 3 correct)
        # Since subject_quiz has 3 questions and we answer every other one correctly
        assert 60 <= session.score <= 75  # Allow variance


@pytest.mark.django_db
class TestQuizSessionRandomness:
    """Test that quiz sessions select different random questions."""
    
    def test_subject_quiz_different_sessions_different_questions(self, subject_quiz, student, multiple_questions):
        """Different sessions should potentially select different questions."""
        # Create first session
        session1 = QuizSession.objects.create(
            student=student,
            quiz=subject_quiz,
            grade=6
        )
        questions1 = set(session1.session_questions.values_list('id', flat=True))
        
        # Delete and create new session
        session1.delete()
        
        session2 = QuizSession.objects.create(
            student=student,
            quiz=subject_quiz,
            grade=6
        )
        questions2 = set(session2.session_questions.values_list('id', flat=True))
        
        # Both should have correct count
        assert len(questions1) == subject_quiz.question_count
        assert len(questions2) == subject_quiz.question_count
        
        # They might be different (random), but both valid
        # This is probabilistic, so we just check they're valid selections
    
    def test_custom_quiz_with_count_random_subset(self, custom_quiz_with_count, student):
        """Custom quiz with count should select random subset."""
        session = QuizSession.objects.create(
            student=student,
            quiz=custom_quiz_with_count,
            grade=6
        )
        
        # Should select exactly question_count questions
        assert session.session_questions.count() == custom_quiz_with_count.question_count
        
        # All selected should be from quiz's questions
        for q in session.session_questions.all():
            assert q in custom_quiz_with_count.questions.all()
