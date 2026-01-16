"""
Unit tests for quizzes app models.
"""
import pytest
from django.utils import timezone

from apps.quizzes.models import Quiz, QuizSession


@pytest.mark.django_db
class TestQuizModel:
    """Test Quiz model functionality"""
    
    def test_create_quiz(self, subject, admin_user):
        """Test creating a quiz"""
        quiz = Quiz.objects.create(
            title='Test Quiz',
            description='A test quiz',
            subject=subject,
            grade=4,
            time_limit_minutes=30,
            passing_score=70,
            created_by=admin_user
        )
        
        assert quiz.title == 'Test Quiz'
        assert quiz.grade == 4
        assert quiz.time_limit_minutes == 30
        assert quiz.passing_score == 70
        assert quiz.is_active is True
    
    def test_quiz_str_representation(self, quiz):
        """Test __str__ method"""
        assert 'Latihan Matematika' in str(quiz)
        assert 'Kelas 4' in str(quiz)
    
    def test_total_points_property(self, quiz_with_questions):
        """Test total_points property"""
        # quiz_with_questions has 1 question with 10 points
        assert quiz_with_questions.total_points == 10
    
    def test_question_count_property(self, quiz_with_questions):
        """Test question_count property"""
        assert quiz_with_questions.question_count == 1
    
    def test_quiz_with_multiple_questions(self, quiz, question, topic, admin_user):
        """Test quiz with multiple questions"""
        from apps.questions.models import Question
        
        # Add more questions
        q2 = Question.objects.create(
            topic=topic,
            question_text='Test question 2',
            question_type='pilgan',
            difficulty='sedang',
            options=['A', 'B', 'C', 'D'],
            answer_key='A',
            points=15,
            created_by=admin_user
        )
        
        quiz.questions.add(question, q2)
        
        assert quiz.question_count == 2
        assert quiz.total_points == 25  # 10 + 15


@pytest.mark.django_db
class TestQuizSessionModel:
    """Test QuizSession model functionality"""
    
    def test_create_quiz_session(self, quiz, student_user):
        """Test creating a quiz session"""
        session = QuizSession.objects.create(
            student=student_user,
            quiz=quiz,
            grade=4,
            score=0
        )
        
        assert session.student == student_user
        assert session.quiz == quiz
        assert session.grade == 4
        assert session.score == 0
        assert session.passed is False
        assert session.is_proxy_mode is False
    
    def test_quiz_session_auto_grade(self, quiz, student_user):
        """Test that grade defaults to student's grade"""
        session = QuizSession.objects.create(
            student=student_user,
            quiz=quiz
        )
        
        assert session.grade == student_user.grade
    
    def test_quiz_session_proxy_mode(self, quiz, student_user, parent_user):
        """Test proxy mode quiz session"""
        session = QuizSession.objects.create(
            student=student_user,
            quiz=quiz,
            is_proxy_mode=True,
            proxy_user=parent_user
        )
        
        assert session.is_proxy_mode is True
        assert session.proxy_user == parent_user
    
    def test_is_completed_property(self, quiz_session):
        """Test is_completed property"""
        assert quiz_session.is_completed is False
        
        quiz_session.completed_at = timezone.now()
        quiz_session.save()
        
        assert quiz_session.is_completed is True
    
    def test_duration_minutes_property(self, quiz_session):
        """Test duration_minutes property"""
        # Not completed yet
        assert quiz_session.duration_minutes is None
        
        # Complete the session
        quiz_session.completed_at = quiz_session.started_at + timezone.timedelta(minutes=15)
        quiz_session.save()
        
        assert quiz_session.duration_minutes == 15
    
    def test_quiz_session_str_representation(self, quiz_session):
        """Test __str__ method"""
        str_repr = str(quiz_session)
        assert 'Student' in str_repr or 'test_student' in str_repr
        assert 'Latihan Matematika' in str_repr
    
    def test_quiz_session_proxy_str_representation(self, quiz, student_user, parent_user):
        """Test __str__ for proxy mode"""
        session = QuizSession.objects.create(
            student=student_user,
            quiz=quiz,
            is_proxy_mode=True,
            proxy_user=parent_user
        )
        
        assert '[PROXY]' in str(session)
    
    def test_quiz_session_scoring(self, quiz_session):
        """Test quiz session scoring"""
        quiz_session.score = 85.5
        quiz_session.passed = True
        quiz_session.save()
        
        assert quiz_session.score == 85.5
        assert quiz_session.passed is True
