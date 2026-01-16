"""
E2E Tests for Parent User Flow
Tests parent functionality including viewing students, selecting students for quizzes,
and taking quizzes in proxy mode.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_login(page: Page, base_url: str, test_users: dict):
    """Test that parent can successfully login"""
    # Navigate to login page
    page.goto(f"{base_url}/accounts/login/")
    
    # Fill credentials
    page.fill("input[name='username']", test_users['parent']['username'])
    page.fill("input[name='password']", test_users['parent']['password'])
    
    # Submit login
    page.click("button[type='submit']")
    
    # Should redirect to dashboard or home
    page.wait_for_url(f"{base_url}/**", timeout=5000)
    
    # Verify we're logged in by checking URL is not login page
    assert "/login" not in page.url
    # Should be on parent dashboard
    assert "/students" in page.url or "/home" in page.url or "/dashboard" in page.url


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_view_students(logged_in_parent_page: Page, base_url: str):
    """Test that parent can view their linked students"""
    page = logged_in_parent_page
    
    # Navigate to students page
    page.goto(f"{base_url}/students/")
    
    # Should see list of students
    # Based on setup_test_data.py, parent has 4 students (grade 3,4,5,6)
    expect(page.locator("text=Andi")).to_be_visible()  # Grade 3 student
    expect(page.locator("text=Budi")).to_be_visible()  # Grade 4 student
    expect(page.locator("text=Citra")).to_be_visible()  # Grade 5 student
    expect(page.locator("text=Dewi")).to_be_visible()  # Grade 6 student


@pytest.mark.e2e
@pytest.mark.parent
@pytest.mark.quiz
def test_parent_can_select_student_for_quiz(logged_in_parent_page: Page, base_url: str):
    """Test that parent can select a student to take a quiz"""
    page = logged_in_parent_page
    
    # Navigate to quizzes page
    page.goto(f"{base_url}/quizzes/student/")
    
    # Should see available quizzes or prompt to select student
    # If there's a student selector, select one
    if page.is_visible("select[name='student']"):
        page.select_option("select[name='student']", label="Budi")  # Grade 4 student
    
    # Should see quizzes for the selected grade
    expect(page.locator("text=Kuis")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.parent
@pytest.mark.quiz
def test_parent_proxy_mode_quiz_taking(logged_in_parent_page: Page, base_url: str):
    """Test that parent can take quiz in proxy mode (on behalf of student)"""
    page = logged_in_parent_page
    
    # Based on setup_test_data.py, there's a quiz for Grade 6 IPA
    # Navigate to quiz list for a specific student
    page.goto(f"{base_url}/quizzes/student/")
    
    # Find and click on a quiz (look for "Mulai" or "Take Quiz" button)
    # This will vary based on your actual UI
    quiz_link = page.locator("a:has-text('Ujian Simulasi IPA')").first
    if quiz_link.is_visible():
        quiz_link.click()
        
        # Wait for quiz page to load
        page.wait_for_load_state("networkidle")
        
        # Should see "Mode Pendampingan" banner indicating proxy mode
        expect(page.locator("text=Mode Pendampingan")).to_be_visible()
        
        # Should see quiz questions
        expect(page.locator("text=Soal")).to_be_visible()
        
        # Should see answer options (radio buttons)
        expect(page.locator("input[type='radio']")).to_be_visible()
        
        # Select an answer for the first question
        page.locator("input[type='radio']").first.check()
        
        # Verify answer is selected
        assert page.locator("input[type='radio']").first.is_checked()


@pytest.mark.e2e
@pytest.mark.parent
@pytest.mark.quiz
def test_parent_can_submit_quiz_for_student(logged_in_parent_page: Page, base_url: str):
    """Test that parent can submit quiz on behalf of student"""
    page = logged_in_parent_page
    
    # Navigate to an active quiz (if exists from setup_test_data)
    # Based on setup_test_data.py line 223, there's an in-progress proxy quiz
    page.goto(f"{base_url}/quizzes/student/")
    
    # Find quiz in progress or start new one
    quiz_button = page.locator("a:has-text('Lanjutkan'), a:has-text('Mulai')").first
    if quiz_button.is_visible():
        quiz_button.click()
        page.wait_for_load_state("networkidle")
        
        # Answer all questions
        radio_buttons = page.locator("input[type='radio']")
        count = radio_buttons.count()
        
        # Select first option for each question (simplified for test)
        for i in range(min(count, 3)):  # Answer up to 3 questions
            try:
                radio_buttons.nth(i * 4).check()  # Assuming 4 options per question
            except:
                pass
        
        # Submit quiz
        submit_button = page.locator("button:has-text('Selesaikan')")
        if submit_button.is_visible():
            # Handle confirmation dialog
            page.on("dialog", lambda dialog: dialog.accept())
            submit_button.click()
            
            # Should redirect to results page
            page.wait_for_url("**/result/**", timeout=10000)
            
            # Should see score or results
            expect(page.locator("text=Skor, text=Nilai, text=Hasil")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_view_student_progress(logged_in_parent_page: Page, base_url: str):
    """Test that parent can view student progress and analytics"""
    page = logged_in_parent_page
    
    # Navigate to analytics or progress page
    # Adjust URL based on your actual routes
    if page.is_visible("a:has-text('Analitik'), a:has-text('Progress')"):
        page.locator("a:has-text('Analitik'), a:has-text('Progress')").first.click()
        
        # Should see some progress indicators
        expect(page.locator("text=Statistik, text=Nilai, text=Progress")).to_be_visible()
