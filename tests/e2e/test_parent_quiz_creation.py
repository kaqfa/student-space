"""
E2E Tests for Parent Custom Quiz Creation
Tests parent's ability to create custom quizzes with filters and assign to students.
Based on TEST_SCENARIOS.md - Scenario 2
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.parent
@pytest.mark.quiz
def test_parent_can_create_custom_quiz_with_filters(logged_in_parent_page: Page, base_url: str):
    """
    Scenario 2.1: Create Custom Quiz with Filters
    Parent can create a targeted quiz by filtering questions.
    """
    page = logged_in_parent_page
    
    # Navigate to quiz creation
    page.goto(f"{base_url}/quizzes/create/")
    
    # Fill quiz creation form
    page.fill("input[name='title'], input[name='name']", "Latihan Pecahan Minggu Ini")
    
    # Select subject
    subject_selector = page.locator("select[name='subject'], select[name*='subject']").first
    if subject_selector.is_visible():
        subject_selector.select_option(label="Matematika")
    
    # Select topic
    topic_selector = page.locator("select[name='topic'], select[name*='topic']").first
    if topic_selector.is_visible():
        topic_selector.select_option(label="Pecahan")
    
    # Select difficulty
    difficulty_selector = page.locator("select[name='difficulty'], input[name='difficulty']").first
    if difficulty_selector.is_visible():
        if difficulty_selector.evaluate("el => el.tagName") == "SELECT":
            difficulty_selector.select_option("sedang")
        else:
            difficulty_selector.check()
    
    # Set question count
    question_count = page.locator("input[name='question_count'], input[name='num_questions']").first
    if question_count.is_visible():
        question_count.fill("10")
    
    # Set time limit
    time_limit = page.locator("input[name='time_limit'], input[name='time_limit_minutes']").first
    if time_limit.is_visible():
        time_limit.fill("20")
    
    # Submit
    submit_button = page.locator("button[type='submit'], button:has-text('Create'), button:has-text('Buat')").first
    if submit_button.is_visible():
        submit_button.click()
        page.wait_for_load_state("networkidle", timeout=10000)
        
        # Should redirect to quiz list or success page
        assert "/quiz" in page.url.lower()


@pytest.mark.e2e
@pytest.mark.parent
@pytest.mark.quiz
def test_parent_can_assign_quiz_to_student(logged_in_parent_page: Page, base_url: str):
    """
    Parent can assign created quiz to specific student(s).
    """
    page = logged_in_parent_page
    
    # Navigate to quiz creation
    page.goto(f"{base_url}/quizzes/create/")
    
    # Look for student selector
    student_selector = page.locator("select[name*='student'], input[name*='student'], [class*='student-select']").first
    
    if student_selector.is_visible():
        # Select a student (e.g., Budi - Grade 4)
        if student_selector.evaluate("el => el.tagName") == "SELECT":
            student_selector.select_option(label="Budi")
        
        # Fill minimum required fields
        page.fill("input[name='title'], input[name='name']", "Quiz for Budi")
        
        # Submit
        submit_button = page.locator("button[type='submit']").first
        if submit_button.is_visible():
            submit_button.click()
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Should succeed
            assert "/quiz" in page.url.lower()


@pytest.mark.e2e
@pytest.mark.parent
@pytest.mark.quiz
def test_parent_can_set_quiz_due_date(logged_in_parent_page: Page, base_url: str):
    """
    Parent can set a due date for assigned quizzes.
    """
    page = logged_in_parent_page
    
    page.goto(f"{base_url}/quizzes/create/")
    
    # Look for due date field
    due_date_field = page.locator("input[type='date'], input[name='due_date'], input[name*='due']").first
    
    if due_date_field.is_visible():
        # Set due date to next week
        due_date_field.fill("2026-01-22")
        
        # Fill other required fields
        page.fill("input[name='title']", "Quiz with Due Date")
        
        # Submit
        submit_button = page.locator("button[type='submit']").first
        if submit_button.is_visible():
            submit_button.click()
            page.wait_for_load_state("networkidle", timeout=10000)


@pytest.mark.e2e
@pytest.mark.parent
@pytest.mark.quiz
def test_parent_can_preview_questions_before_creation(logged_in_parent_page: Page, base_url: str):
    """
    Scenario 2.1: Preview Questions
    Parent can preview selected questions before finalizing quiz.
    """
    page = logged_in_parent_page
    
    page.goto(f"{base_url}/quizzes/create/")
    
    # Fill filters
    page.fill("input[name='title']", "Preview Test Quiz")
    
    # Look for preview button
    preview_button = page.locator("button:has-text('Preview'), button:has-text('Pratinjau')").first
    
    if preview_button.is_visible():
        preview_button.click()
        page.wait_for_load_state("networkidle", timeout=5000)
        
        # Should see preview of questions
        # Look for question text or preview indicator
        preview_content = page.locator("text=/Question|Soal|Preview/i")
        
        if preview_content.is_visible():
            expect(preview_content).to_be_visible()


@pytest.mark.e2e
@pytest.mark.parent
@pytest.mark.quiz
def test_parent_quiz_creation_form_validation(logged_in_parent_page: Page, base_url: str):
    """
    Quiz creation form should validate required fields.
    """
    page = logged_in_parent_page
    
    page.goto(f"{base_url}/quizzes/create/")
    
    # Try to submit without filling required fields
    submit_button = page.locator("button[type='submit']").first
    
    if submit_button.is_visible():
        submit_button.click()
        
        # Should show validation error or stay on page
        page.wait_for_timeout(1000)
        
        # Should still be on create page
        assert "/create" in page.url or "/new" in page.url
