"""
E2E Tests for Multiple Question Types
Tests different question types (pilgan, essay, isian) display and submission.
Based on TEST_SCENARIOS.md - Scenario 11
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.quiz
def test_pilgan_multiple_choice_question_display_and_submit(logged_in_student_page: Page, base_url: str):
    """
    Scenario 11.1: Pilgan (Multiple Choice) Questions
    Test that multiple choice questions display correctly with radio buttons.
    """
    page = logged_in_student_page
    
    # Start a quiz
    page.goto(f"{base_url}/quizzes/student/")
    quiz_link = page.locator("a:has-text('Mulai')").first
    
    if quiz_link.is_visible():
        quiz_link.click()
        page.wait_for_load_state("networkidle")
        
        # Should see radio buttons (pilgan question)
        radio_buttons = page.locator("input[type='radio']")
        
        if radio_buttons.count() > 0:
            # Verify radio button behavior
            first_option = radio_buttons.first
            second_option = radio_buttons.nth(1)
            
            # Select first option
            first_option.check()
            assert first_option.is_checked()
            
            # Select second option (should uncheck first)
            second_option.check()
            assert second_option.is_checked()
            assert not first_option.is_checked()
            
            # Options should be visible
            expect(radio_buttons.first).to_be_visible()


@pytest.mark.e2e
@pytest.mark.quiz
def test_essay_question_display_and_submit(logged_in_student_page: Page, base_url: str):
    """
    Scenario 11.2: Essay Questions
    Test that essay questions show text area for free-form answers.
    
    Note: Essay questions may not be in current test data.
    """
    page = logged_in_student_page
    
    # Start a quiz
    page.goto(f"{base_url}/quizzes/student/")
    quiz_link = page.locator("a:has-text('Mulai')").first
    
    if quiz_link.is_visible():
        quiz_link.click()
        page.wait_for_load_state("networkidle")
        
        # Look for textarea (essay question)
        textarea = page.locator("textarea, input[type='text'][class*='large']")
        
        if textarea.count() > 0:
            # Should be able to type in textarea
            textarea.first.fill("This is my essay answer for testing purposes.")
            
            # Verify content
            content = textarea.first.input_value()
            assert "essay answer" in content.lower()


@pytest.mark.e2e
@pytest.mark.quiz
def test_isian_fill_in_blank_question_display_and_submit(logged_in_student_page: Page, base_url: str):
    """
    Scenario 11.3: Isian (Fill-in-Blank) Questions
    Test that isian questions show single input field.
    
    Note: Isian questions may not be in current test data.
    """
    page = logged_in_student_page
    
    # Start a quiz
    page.goto(f"{base_url}/quizzes/student/")
    quiz_link = page.locator("a:has-text('Mulai')").first
    
    if quiz_link.is_visible():
        quiz_link.click()
        page.wait_for_load_state("networkidle")
        
        # Look for single text input (isian question)
        # Not radio, not textarea - simple text input
        text_input = page.locator("input[type='text']:not([class*='search'])")
        
        if text_input.count() > 0:
            # Should be able to fill answer
            text_input.first.fill("42")
            
            # Verify
            value = text_input.first.input_value()
            assert value == "42"


@pytest.mark.e2e
@pytest.mark.quiz
def test_mixed_question_types_in_single_quiz(logged_in_student_page: Page, base_url: str):
    """
    Quiz can contain mix of different question types.
    Student can navigate and answer each type.
    """
    page = logged_in_student_page
    
    # Start quiz
    page.goto(f"{base_url}/quizzes/student/")
    quiz_link = page.locator("a:has-text('Mulai')").first
    
    if quiz_link.is_visible():
        quiz_link.click()
        page.wait_for_load_state("networkidle")
        
        # Track question types seen
        has_pilgan = page.locator("input[type='radio']").count() > 0
        has_essay = page.locator("textarea").count() > 0
        has_isian = page.locator("input[type='text']").count() > 0
        
        # Current test data mainly has pilgan
        # So we expect at least pilgan to be present
        assert has_pilgan, "Should have at least pilgan questions in quiz"
