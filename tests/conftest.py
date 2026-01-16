"""
Pytest configuration and fixtures for both E2E and unit testing.
"""
import os
import django

# Setup Django before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

import pytest
from playwright.sync_api import Page


# ============================================================
# E2E Test Fixtures (Playwright)
# ============================================================

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application"""
    return "http://127.0.0.1:8000"


@pytest.fixture
def test_users():
    """Return test user credentials from setup_test_data"""
    return {
        'admin': {'username': 'admin', 'password': 'admin123'},
        'parent': {'username': 'orangtua', 'password': 'parent123'},
        'student_grade3': {'username': 'siswa3', 'password': 'siswa123'},
        'student_grade4': {'username': 'siswa4', 'password': 'siswa123'},
        'student_grade5': {'username': 'siswa5', 'password': 'siswa123'},
        'student_grade6': {'username': 'siswa6', 'password': 'siswa123'},
    }


@pytest.fixture
def login_as_parent(page: Page, base_url: str, test_users: dict):
    """Helper fixture to login as parent"""
    def _login():
        page.goto(f"{base_url}/accounts/login/")
        page.fill("input[name='username']", test_users['parent']['username'])
        page.fill("input[name='password']", test_users['parent']['password'])
        page.click("button[type='submit']")
        page.wait_for_url(f"{base_url}/**")  # Wait for redirect after login
        return page
    return _login


@pytest.fixture
def login_as_student(page: Page, base_url: str, test_users: dict):
    """Helper fixture to login as student (default: grade 4)"""
    def _login(grade: int = 4):
        page.goto(f"{base_url}/accounts/login/")
        page.fill("input[name='username']", test_users[f'student_grade{grade}']['username'])
        page.fill("input[name='password']", test_users[f'student_grade{grade}']['password'])
        page.click("button[type='submit']")
        page.wait_for_url(f"{base_url}/**")  # Wait for redirect after login
        return page
    return _login


@pytest.fixture
def logged_in_parent_page(page: Page, login_as_parent):
    """Fixture that returns a page already logged in as parent"""
    login_as_parent()
    return page


@pytest.fixture
def logged_in_student_page(page: Page, login_as_student):
    """Fixture that returns a page already logged in as student (grade 4)"""
    login_as_student(grade=4)
    return page


# ============================================================
# Unit Test Fixtures (pytest-django)
# ============================================================

@pytest.fixture
def admin_user(db):
    """Create an admin user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    return User.objects.create_user(
        username='test_admin',
        email='admin@test.com',
        password='testpass123',
        role=User.Role.ADMIN,
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def parent_user(db):
    """Create a parent user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    return User.objects.create_user(
        username='test_parent',
        email='parent@test.com',
        password='testpass123',
        role=User.Role.PARENT,
        first_name='Parent',
        last_name='User'
    )


@pytest.fixture
def student_user(db):
    """Create a student user (grade 4)"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    return User.objects.create_user(
        username='test_student',
        email='student@test.com',
        password='testpass123',
        role=User.Role.STUDENT,
        grade=4,
        first_name='Student',
        last_name='User'
    )


@pytest.fixture
def student_grade6(db):
    """Create a grade 6 student"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    return User.objects.create_user(
        username='test_student_6',
        email='student6@test.com',
        password='testpass123',
        role=User.Role.STUDENT,
        grade=6,
        first_name='Student',
        last_name='Grade6'
    )


@pytest.fixture
def subject(db):
    """Create a test subject"""
    from apps.subjects.models import Subject
    
    return Subject.objects.create(
        name='Matematika',
        grade=4,
        order=1,
        color='#3B82F6'
    )


@pytest.fixture
def topic(db, subject):
    """Create a test topic"""
    from apps.subjects.models import Topic
    
    return Topic.objects.create(
        subject=subject,
        name='Pecahan',
        description='Belajar tentang pecahan',
        order=1
    )


@pytest.fixture
def tag(db):
    """Create a test tag"""
    from apps.questions.models import Tag
    
    return Tag.objects.create(
        name='operasi-hitung',
        category=Tag.Category.SKILL
    )


@pytest.fixture
def kompetensi_dasar(db, subject):
    """Create a test KD"""
    from apps.questions.models import KompetensiDasar
    
    return KompetensiDasar.objects.create(
        code='3.1',
        description='Memahami pecahan sederhana',
        grade=4,
        subject=subject
    )


@pytest.fixture
def question(db, topic, admin_user):
    """Create a test question (pilgan)"""
    from apps.questions.models import Question
    
    return Question.objects.create(
        topic=topic,
        question_text='Berapa hasil dari 1/2 + 1/4?',
        question_type='pilgan',
        difficulty='mudah',
        options=['1/2', '3/4', '1/4', '1'],
        answer_key='B',
        explanation='1/2 + 1/4 = 2/4 + 1/4 = 3/4',
        points=10,
        estimated_time=60,
        created_by=admin_user
    )


@pytest.fixture
def quiz(db, subject, admin_user):
    """Create a test quiz"""
    from apps.quizzes.models import Quiz
    
    return Quiz.objects.create(
        title='Latihan Matematika Kelas 4',
        description='Latihan soal pecahan',
        subject=subject,
        grade=4,
        time_limit_minutes=30,
        passing_score=70,
        created_by=admin_user
    )


@pytest.fixture
def quiz_with_questions(db, quiz, question):
    """Create a quiz with questions"""
    quiz.questions.add(question)
    return quiz


@pytest.fixture
def quiz_session(db, quiz, student_user):
    """Create a quiz session"""
    from apps.quizzes.models import QuizSession
    
    return QuizSession.objects.create(
        student=student_user,
        quiz=quiz,
        grade=student_user.grade,
        score=0
    )


@pytest.fixture
def parent_student_link(db, parent_user, student_user):
    """Create an approved parent-student link"""
    from apps.accounts.models import ParentStudent
    
    return ParentStudent.create_with_new_student(
        parent=parent_user,
        student=student_user
    )


@pytest.fixture
def authenticated_client(client, student_user):
    """Return a Django test client authenticated as student"""
    client.force_login(student_user)
    return client


@pytest.fixture
def parent_client(client, parent_user):
    """Return a Django test client authenticated as parent"""
    client.force_login(parent_user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Return a Django test client authenticated as admin"""
    client.force_login(admin_user)
    return client
