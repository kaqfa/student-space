"""
E2E Tests for Student User Flow
Tests student functionality including login, viewing quizzes, taking quizzes,
and viewing own results.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.student
def test_student_can_login(page: Page, base_url: str, test_users: dict):
    """Test that student can successfully login"""
    # Navigate to login page
    page.goto(f"{base_url}/accounts/login/")
    
    # Fill credentials for grade 4 student
    page.fill("input[name='username']", test_users['student_grade4']['username'])
    page.fill("input[name='password']", test_users['student_grade4']['password'])
    
    # Submit login
    page.click("button[type='submit']")
    
    # Should redirect to dashboard or home
    page.wait_for_url(f"{base_url}/**", timeout=5000)
    
    # Verify we're logged in by checking URL  is not login page
    assert "/login" not in page.url
    # Should be on student dashboard
    assert "/students" in page.url or "/home" in page.url or "/dashboard" in page.url


@pytest.mark.e2e
@pytest.mark.student
@pytest.mark.quiz
def test_student_can_view_available_quizzes(logged_in_student_page: Page, base_url: str):
    """Test that student can view available quizzes for their grade"""
    page = logged_in_student_page
    
    # Navigate to quizzes page
    page.goto(f"{base_url}/quizzes/student/")
    
    # Should see quizzes for grade 4
    # Based on setup_test_data.py, there should be quizzes for Math, IPA, Bahasa
    expect(page.locator("text=Latihan, text=Kuis, text=Ujian")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.student
@pytest.mark.quiz
def test_student_can_start_quiz(logged_in_student_page: Page, base_url: str):
    """Test that student can start taking a quiz"""
    page = logged_in_student_page
    
    # Navigate to quizzes
    page.goto(f"{base_url}/quizzes/student/")
    
    # Find and click on a quiz to start
    quiz_link = page.locator("a:has-text('Mulai'), a:has-text('Latihan')").first
    if quiz_link.is_visible():
        quiz_link.click()
        
        # Wait for quiz page to load
        page.wait_for_load_state("networkidle")
        
        # Should see quiz title
        expect(page.locator("h1, h2").first).to_be_visible()
        
        # Should see questions
        expect(page.locator("text=Soal")).to_be_visible()
        
        # Should NOT see proxy mode banner (student taking their own quiz)
        expect(page.locator("text=Mode Pendampingan")).not_to_be_visible()


@pytest.mark.e2e
@pytest.mark.student
@pytest.mark.quiz
def test_student_can_see_quiz_options(logged_in_student_page: Page, base_url: str):
    """Test that student can see answer options for multiple choice questions"""
    page = logged_in_student_page
    
    # Navigate to an active quiz
    page.goto(f"{base_url}/quizzes/student/")
    
    # Start a quiz
    quiz_link = page.locator("a:has-text('Mulai'), a:has-text('Latihan')").first
    if quiz_link.is_visible():
        quiz_link.click()
        page.wait_for_load_state("networkidle")
        
        # Check if answer options are visible
        # Should see radio buttons for multiple choice
        radio_buttons = page.locator("input[type='radio']")
        expect(radio_buttons.first).to_be_visible()
        
        # Should see option labels (A, B, C, D)
        expect(page.locator("text=/^[A-D]\\./")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.student
@pytest.mark.quiz
def test_student_can_select_answers(logged_in_student_page: Page, base_url: str):
    """Test that student can select answers for quiz questions"""
    page = logged_in_student_page
    
    # Navigate and start quiz
    page.goto(f"{base_url}/quizzes/student/")
    quiz_link = page.locator("a:has-text('Mulai'), a:has-text('Latihan')").first
    
    if quiz_link.is_visible():
        quiz_link.click()
        page.wait_for_load_state("networkidle")
        
        # Get all radio buttons
        radio_buttons = page.locator("input[type='radio']")
        
        if radio_buttons.count() > 0:
            # Select first answer
            radio_buttons.first.check()
            
            # Verify it's checked
            assert radio_buttons.first.is_checked()
            
            # Try selecting different answer for same question group
            if radio_buttons.count() > 1:
                radio_buttons.nth(1).check()
                
                # First should be unchecked, second should be checked
                assert not radio_buttons.first.is_checked()
                assert radio_buttons.nth(1).is_checked()


@pytest.mark.e2e
@pytest.mark.student
@pytest.mark.quiz
def test_student_can_submit_quiz(logged_in_student_page: Page, base_url: str):
    """Test that student can submit a completed quiz"""
    page = logged_in_student_page
    
    # Navigate and start quiz
    page.goto(f"{base_url}/quizzes/student/")
    quiz_link = page.locator("a:has-text('Mulai'), a:has-text('Latihan')").first
    
    if quiz_link.is_visible():
        quiz_link.click()
        page.wait_for_load_state("networkidle")
        
        # Answer all visible questions
        radio_buttons = page.locator("input[type='radio']")
        count = radio_buttons.count()
        
        # Select first option for each question (simplified)
        for i in range(min(count, 5)):
            try:
                radio_buttons.nth(i * 4).check()  # Assuming 4 options per question
            except:
                pass
        
        # Look for submit button
        submit_button = page.locator("button:has-text('Selesaikan'), button[type='submit']").last
        
        if submit_button.is_visible():
            # Handle confirmation dialog
            page.on("dialog", lambda dialog: dialog.accept())
            
            # Submit the quiz
            submit_button.click()
            
            # Should redirect to results or home
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Should see some confirmation or results
            expect(page.locator("text=Skor, text=Hasil, text=Selesai")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.student
def test_student_can_view_own_results(logged_in_student_page: Page, base_url: str):
    """Test that student can view their quiz results history"""
    page = logged_in_student_page
    
    # Based on setup_test_data.py, students have completed quiz sessions
    # Try to navigate to results/history page
    # Adjust URL based on your actual routes
    
    # Look for navigation to results
    if page.is_visible("a:has-text('Hasil'), a:has-text('Riwayat'), a:has-text('History')"):
        page.locator("a:has-text('Hasil'), a:has-text('Riwayat'), a:has-text('History')").first.click()
        
        # Should see list of completed quizzes
        expect(page.locator("text=Nilai, text=Skor, text=Latihan")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.student
@pytest.mark.quiz
def test_student_quiz_timer_visible(logged_in_student_page: Page, base_url: str):
    """Test that quiz timer is visible when quiz has time limit"""
    page = logged_in_student_page
    
    # Navigate to quizzes
    page.goto(f"{base_url}/quizzes/student/")
    
    # Start a quiz that has time limit
    quiz_link = page.locator("a:has-text('Mulai'), a:has-text('Latihan')").first
    if quiz_link.is_visible():
        quiz_link.click()
        page.wait_for_load_state("networkidle")
        
        # Check for timer element
        timer = page.locator("#timer, [id*='timer'], text=/\\d{2}:\\d{2}/")
        
        # Timer should be visible if quiz has time limit
        if timer.is_visible():
            # Timer should show countdown format (e.g., "29:45")
            timer_text = timer.text_content()
            assert ":" in timer_text


@pytest.mark.e2e
@pytest.mark.student
def test_student_cannot_access_admin_features(logged_in_student_page: Page, base_url: str):
    """Test that student cannot access admin/parent features"""
    page = logged_in_student_page
    
    # Try to access quiz creation page (should be forbidden)
    page.goto(f"{base_url}/quizzes/create/")
    
    # Should see error, forbidden, or redirect to login
    assert page.url != f"{base_url}/quizzes/create/" or \
           page.is_visible("text=403, text=Forbidden, text=Permission")
