"""
End-to-End tests for Quiz workflows using Playwright.
Tests complete user journeys from UI perspective.
"""
import pytest
from playwright.sync_api import Page, expect
from apps.quizzes.models import Quiz, QuizSession
from apps.analytics.models import Attempt


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
class TestAdminQuizCreation:
    """Test admin quiz creation workflow through UI."""
    
    def test_admin_create_subject_quiz_full_flow(self, page: Page, live_server, admin_user, subject, multiple_questions):
        """Admin creates subject quiz through UI."""
        # Login as admin
        page.goto(f"{live_server.url}/accounts/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')
        
        # Navigate to quiz admin
        page.goto(f"{live_server.url}/admin/quizzes/quiz/")
        
        # Click create subject quiz link
        page.click('text=Subject Quiz (Random Questions)')
        
        # Fill form
        page.fill('input[name="title"]', 'E2E Subject Quiz')
        page.fill('textarea[name="description"]', 'Created via E2E test')
        page.select_option('select[name="subject"]', str(subject.id))
        page.select_option('select[name="grade"]', '6')
        page.fill('input[name="question_count"]', '3')
        page.fill('input[name="time_limit_minutes"]', '30')
        page.fill('input[name="passing_score"]', '70')
        
        # Submit
        page.click('button[type="submit"]')
        
        # Verify quiz created
        quiz = Quiz.objects.get(title='E2E Subject Quiz')
        assert quiz.quiz_type == Quiz.QuizType.SUBJECT_BASED
        assert quiz.question_count == 3
    
    def test_admin_create_custom_quiz_full_flow(self, page: Page, live_server, admin_user, subject, multiple_questions):
        """Admin creates custom quiz through UI."""
        # Login
        page.goto(f"{live_server.url}/accounts/login/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')
        
        # Navigate to quiz admin
        page.goto(f"{live_server.url}/admin/quizzes/quiz/")
        
        # Click create custom quiz
        page.click('text=Custom Quiz (Select Questions)')
        
        # Select first 3 questions
        for i in range(3):
            page.locator('button:has-text("Pilih")').first.click()
            page.wait_for_timeout(500)  # Wait for redirect
            page.goto(f"{live_server.url}/quizzes/create/custom/")  # Go back
        
        # Fill quiz info
        page.fill('input[name="title"]', 'E2E Custom Quiz')
        page.select_option('select[name="subject"]', str(subject.id))
        page.select_option('select[name="grade"]', '6')
        page.fill('input[name="question_count"]', '2')  # Random 2 from 3 selected
        page.fill('input[name="time_limit_minutes"]', '20')
        page.fill('input[name="passing_score"]', '60')
        
        # Submit
        page.click('button:has-text("Buat Custom Quiz")')
        
        # Verify quiz created
        quiz = Quiz.objects.get(title='E2E Custom Quiz')
        assert quiz.quiz_type == Quiz.QuizType.CUSTOM
        assert quiz.question_count == 2
        assert quiz.questions.count() == 3


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
class TestStudentQuizTaking:
    """Test student quiz taking workflow through UI."""
    
    def test_student_take_quiz_full_flow(self, page: Page, live_server, student, subject_quiz):
        """Student takes quiz and submits answers."""
        # Login as student
        page.goto(f"{live_server.url}/accounts/login/")
        page.fill('input[name="username"]', 'student')
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')
        
        # Navigate to available quizzes
        page.goto(f"{live_server.url}/quizzes/available/")
        
        # Click on quiz
        page.click(f'text={subject_quiz.title}')
        
        # Verify session created with attempts
        session = QuizSession.objects.get(student=student, quiz=subject_quiz)
        assert session.session_questions.count() == subject_quiz.question_count
        
        attempts_count = Attempt.objects.filter(quiz_session=session).count()
        assert attempts_count == subject_quiz.question_count
        
        # Fill answers (select first option for all questions)
        questions = session.session_questions.all()
        for question in questions:
            # Look for radio button or select for this question
            locator = page.locator(f'input[name="question_{question.id}"]').first
            if locator.count() > 0:
                locator.click()
        
        # Submit quiz
        page.click('button[type="submit"]:has-text("Submit")', timeout=5000)
        
        # Verify completion
        session.refresh_from_db()
        assert session.completed_at is not None
        
        # Verify attempts updated
        attempts = Attempt.objects.filter(quiz_session=session)
        # At least some should have answers (depends on which we clicked)
        answered = [a for a in attempts if a.answer_given != '']
        assert len(answered) > 0
    
    def test_quiz_session_persistence(self, page: Page, live_server, student, subject_quiz):
        """Quiz session should persist if student refreshes page."""
        # Login
        page.goto(f"{live_server.url}/accounts/login/")
        page.fill('input[name="username"]', 'student')
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')
        
        # Start quiz
        page.goto(f"{live_server.url}/quizzes/{subject_quiz.pk}/take/")
        
        # Get session
        session = QuizSession.objects.get(student=student, quiz=subject_quiz)
        question_ids_before = set(session.session_questions.values_list('id', flat=True))
        
        # Refresh page
        page.reload()
        
        # Session should still exist with same questions
        session.refresh_from_db()
        question_ids_after = set(session.session_questions.values_list('id', flat=True))
        
        assert question_ids_before == question_ids_after


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
class TestQuizResults:
    """Test quiz results display."""
    
    def test_view_quiz_results(self, page: Page, live_server, student, completed_quiz_session):
        """Student can view quiz results after completion."""
        session = completed_quiz_session
        
        # Login
        page.goto(f"{live_server.url}/accounts/login/")
        page.fill('input[name="username"]', 'student')
        page.fill('input[name="password"]', 'password123')
        page.click('button[type="submit"]')
        
        # Navigate to results
        page.goto(f"{live_server.url}/quizzes/{session.quiz.pk}/result/")
        
        # Verify results displayed
        expect(page.locator('text=Skor')).to_be_visible()
        expect(page.locator(f'text={session.quiz.title}')).to_be_visible()
        
        # Score should be displayed
        score_text = str(int(session.score))
        expect(page.locator(f'text={score_text}')).to_be_visible()
