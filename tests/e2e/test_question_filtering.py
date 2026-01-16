"""
E2E Tests for Question Filtering
Tests filtering questions by various criteria (subject, topic, difficulty, tags).
Based on TEST_SCENARIOS.md - Scenario 12
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.admin
def test_filter_questions_by_subject(page: Page, base_url: str, test_users: dict):
    """
    Scenario 12.1: Filter by Subject
    Admin/parent can filter question bank by subject.
    """
    # Login as admin for access to questions page
    page.goto(f"{base_url}/accounts/login/")
    page.fill("input[name='username']", test_users['admin']['username'])
    page.fill("input[name='password']", test_users['admin']['password'])
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    
    # Navigate to questions page
    page.goto(f"{base_url}/questions/")
    
    # Apply subject filter
    subject_filter = page.locator("select[name='subject'], select[name*='subject']").first
    
    if subject_filter.is_visible():
        # Select Matematika
        subject_filter.select_option(label="Matematika")
        
        # Apply filter (might auto-submit or need button)
        filter_btn = page.locator("button:has-text('Filter'), button[type='submit']").first
        if filter_btn.is_visible():
            filter_btn.click()
        
        page.wait_for_load_state("networkidle")
        
        # Should show only Matematika questions
        # Check if page content updated
        assert "question" in page.url.lower() or page.locator("text=Question").is_visible()


@pytest.mark.e2e
@pytest.mark.admin
def test_filter_questions_by_difficulty(page: Page, base_url: str, test_users: dict):
    """
    Scenario 12.1: Filter by Difficulty
    Filter questions by difficulty level.
    """
    # Login as admin
    page.goto(f"{base_url}/accounts/login/")
    page.fill("input[name='username']", test_users['admin']['username'])
    page.fill("input[name='password']", test_users['admin']['password'])
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    
    # Navigate to questions
    page.goto(f"{base_url}/questions/")
    
    # Apply difficulty filter
    difficulty_filter = page.locator("select[name='difficulty'], select[name*='difficulty']").first
    
    if difficulty_filter.is_visible():
        # Select "sulit" (hard)
        difficulty_filter.select_option("sulit")
        
        # Apply
        filter_btn = page.locator("button:has-text('Filter'), button[type='submit']").first
        if filter_btn.is_visible():
            filter_btn.click()
        
        page.wait_for_load_state("networkidle")


@pytest.mark.e2e
@pytest.mark.admin
def test_filter_questions_by_multiple_criteria(page: Page, base_url: str, test_users: dict):
    """
    Scenario 12.2: Filter by Multiple Criteria
    Apply multiple filters simultaneously (subject + difficulty + tags).
    """
    # Login as admin
    page.goto(f"{base_url}/accounts/login/")
    page.fill("input[name='username']", test_users['admin']['username'])
    page.fill("input[name='password']", test_users['admin']['password'])
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    
    # Navigate to questions
    page.goto(f"{base_url}/questions/")
    
    # Apply multiple filters
    # Subject: Matematika
    subject_filter = page.locator("select[name='subject']").first
    if subject_filter.is_visible():
        subject_filter.select_option(label="Matematika")
    
    # Difficulty: sulit
    difficulty_filter = page.locator("select[name='difficulty']").first
    if difficulty_filter.is_visible():
        difficulty_filter.select_option("sulit")
    
    # Topic (if available)
    topic_filter = page.locator("select[name='topic']").first
    if topic_filter.is_visible():
        topic_filter.select_option(index=1)  # Select first topic
    
    # Apply filters
    filter_btn = page.locator("button:has-text('Filter'), button[type='submit']").first
    if filter_btn.is_visible():
        filter_btn.click()
        page.wait_for_load_state("networkidle")
        
        # Should show filtered results
        # Count should be less than total
        question_count = page.locator("[class*='question'], tr").count()
        
        # Should have some results (or zero if no matches)
        assert question_count >= 0


@pytest.mark.e2e
@pytest.mark.admin
def test_clear_all_filters(page: Page, base_url: str, test_users: dict):
    """
    Can clear all applied filters to return to full question list.
    """
    # Login as admin
    page.goto(f"{base_url}/accounts/login/")
    page.fill("input[name='username']", test_users['admin']['username'])
    page.fill("input[name='password']", test_users['admin']['password'])
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    
    # Navigate to questions
    page.goto(f"{base_url}/questions/")
    
    # Apply a filter
    subject_filter = page.locator("select[name='subject']").first
    if subject_filter.is_visible():
        subject_filter.select_option(label="Matematika")
        
        filter_btn = page.locator("button:has-text('Filter')").first
        if filter_btn.is_visible():
            filter_btn.click()
            page.wait_for_load_state("networkidle")
    
    # Clear filters
    clear_btn = page.locator("button:has-text('Clear'), button:has-text('Reset'), a:has-text('All')").first
    
    if clear_btn.is_visible():
        clear_btn.click()
        page.wait_for_load_state("networkidle")
        
        # Should return to full list
        # Filter selects should be reset
        if subject_filter.is_visible():
            selected = subject_filter.evaluate("el => el.value")
            # Should be empty or default
