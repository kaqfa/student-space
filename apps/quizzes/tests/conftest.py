"""
Pytest fixtures for quiz logic tests.
"""
import pytest
from django.test import Client
from apps.quizzes.models import Quiz, QuizSession
from apps.subjects.models import Subject, Topic
from apps.questions.models import Question
from apps.accounts.models import User


@pytest.fixture
def admin_user(db):
    """Create admin user."""
    return User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='password123',
        role=User.Role.ADMIN
    )


@pytest.fixture
def student(db):
    """Create student user."""
    return User.objects.create_user(
        username='student',
        email='student@test.com',
        password='password123',
        role=User.Role.STUDENT,
        grade=6
    )


@pytest.fixture
def subject(db):
    """Create a subject."""
    return Subject.objects.create(
        name='Matematika',
        grade=6
    )


@pytest.fixture
def topic(subject):
    """Create a topic."""
    return Topic.objects.create(
        name='Pecahan',
        subject=subject
    )


@pytest.fixture
def question(topic):
    """Create a single question."""
    return Question.objects.create(
        topic=topic,
        question_text='1/2 + 1/4 = ?',
        question_type='pilgan',
        difficulty='mudah',
        options=['1/2', '3/4', '1/4', '1'],
        answer_key='B',
        points=10
    )


@pytest.fixture
def multiple_questions(topic):
    """Create multiple questions."""
    questions = []
    for i in range(5):
        q = Question.objects.create(
            topic=topic,
            question_text=f'Test question {i+1}',
            question_type='pilgan',
            difficulty='mudah',
            options=['A', 'B', 'C', 'D'],
            answer_key='A',
            points=10
        )
        questions.append(q)
    return questions


@pytest.fixture
def subject_quiz(subject, admin_user, multiple_questions):
    """Create a subject-based quiz."""
    return Quiz.objects.create(
        title='Subject Quiz Test',
        subject=subject,
        grade=6,
        quiz_type=Quiz.QuizType.SUBJECT_BASED,
        question_count=3,
        time_limit_minutes=30,
        passing_score=70,
        created_by=admin_user
    )


@pytest.fixture
def custom_quiz_with_count(subject, admin_user, multiple_questions):
    """Create a custom quiz with question_count."""
    quiz = Quiz.objects.create(
        title='Custom Quiz with Count',
        subject=subject,
        grade=6,
        quiz_type=Quiz.QuizType.CUSTOM,
        question_count=3,  # Select 3 random from 5
        time_limit_minutes=30,
        passing_score=70,
        created_by=admin_user
    )
    quiz.questions.set(multiple_questions)
    return quiz


@pytest.fixture
def custom_quiz_all_questions(subject, admin_user, multiple_questions):
    """Create a custom quiz without question_count (use all)."""
    quiz = Quiz.objects.create(
        title='Custom Quiz All Questions',
        subject=subject,
        grade=6,
        quiz_type=Quiz.QuizType.CUSTOM,
        question_count=None,  # Use all questions
        time_limit_minutes=30,
        passing_score=70,
        created_by=admin_user
    )
    quiz.questions.set(multiple_questions)
    return quiz


@pytest.fixture
def quiz_session_with_attempts(subject_quiz, student):
    """Create a quiz session with pre-generated attempts."""
    return QuizSession.objects.create(
        student=student,
        quiz=subject_quiz,
        grade=6
    )


@pytest.fixture
def admin_client(admin_user):
    """Authenticated admin client."""
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def student_client(student):
    """Authenticated student client."""
    client = Client()
    client.force_login(student)
    return client
