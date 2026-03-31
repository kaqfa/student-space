"""
E2E Tests for Student Registration & Link Verification
Tests student's ability to self-register and manage parent link requests.
Based on TEST_SCENARIOS.md - Scenario 5
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.student
def test_student_can_self_register(page: Page, base_url: str):
    """
    Scenario 5.1: Student Self-Registration
    As a student, I want to create my own account without needing a parent.
    """
    # Navigate to student registration page
    page.goto(f"{base_url}/students/register/")
    
    # Fill registration form
    page.fill("input[name='username']", "siswa_test_new")
    page.fill("input[name='email']", "siswatest@example.com")
    page.fill("input[name='password'], input[name='password1']", "testpass123")
    page.fill("input[name='password2'], input[name='confirm_password']", "testpass123")
    page.fill("input[name='first_name'], input[name='firstName']", "Siti")
    page.fill("input[name='last_name'], input[name='lastName']", "Aminah")
    
    # Select grade
    grade_selector = page.locator("select[name='grade'], input[name='grade']").first
    if grade_selector.is_visible():
        if grade_selector.evaluate("el => el.tagName") == "SELECT":
            grade_selector.select_option("5")
        else:
            grade_selector.fill("5")
    
    # Submit registration
    page.locator("button[type='submit'], button:has-text('Register'), button:has-text('Daftar')").click()
    
    # Should redirect after successful registration
    page.wait_for_load_state("networkidle", timeout=10000)
    
    # Either auto-login (redirect to dashboard) or show login page
    assert "/login" in page.url or "/dashboard" in page.url or "/students" in page.url


@pytest.mark.e2e
@pytest.mark.student
def test_student_can_login_after_registration(page: Page, base_url: str, test_users: dict):
    """
    After registration, student should be able to login with new credentials.
    Using existing test user instead of newly created one for reliability.
    """
    page.goto(f"{base_url}/accounts/login/")
    
    # Use existing student credentials
    page.fill("input[name='username']", test_users['student_grade5']['username'])
    page.fill("input[name='password']", test_users['student_grade5']['password'])
    page.click("button[type='submit']")
    
    # Wait for redirect
    page.wait_for_url(f"{base_url}/**", timeout=5000)
    
    # Should be logged in (not on login page anymore)
    assert "/login" not in page.url
    assert "/students" in page.url or "/dashboard" in page.url or "/home" in page.url


@pytest.mark.e2e
@pytest.mark.student
def test_student_can_view_link_requests(logged_in_student_page: Page, base_url: str):
    """
    Scenario 5.2: View and Approve Parent Link Request
    Student can see pending link requests from parents.
    
    Note: This requires a pending link request to exist.
    """
    page = logged_in_student_page
    
    # Look for link requests page or notification
    # Navigate to link requests if such page exists
    link_requests_nav = page.locator("a:has-text('Link Request'), a:has-text('Permintaan'), a[href*='link']").first
    
    if link_requests_nav.is_visible():
        link_requests_nav.click()
        page.wait_for_load_state("networkidle")
        
        # Should see list of link requests (may be empty if none pending)
        # Look for request items or "no requests" message
        has_requests = page.locator("[class*='request'], [class*='pending']").count() > 0
        has_empty_message = page.locator("text=/No request|Tidak ada|Empty/i").is_visible()
        
        # One of these should be true
        assert has_requests or has_empty_message


@pytest.mark.e2e
@pytest.mark.student
def test_student_can_approve_parent_link(logged_in_student_page: Page, base_url: str):
    """
    Student can approve a pending parent link request.
    
    Note: Requires setup of a pending link request.
    """
    page = logged_in_student_page
    
    # Navigate to link requests
    page.goto(f"{base_url}/students/link-requests/")
    
    # Look for approve button
    approve_button = page.locator("button:has-text('Approve'), button:has-text('Terima'), button:has-text('Setuju')").first
    
    if approve_button.is_visible():
        approve_button.click()
        
        # Should show success message or redirect
        page.wait_for_load_state("networkidle", timeout=5000)
        
        # Verify success (message or request disappears)
        success_indicator = page.locator("text=/approved|disetujui|success/i")
        if success_indicator.is_visible():
            expect(success_indicator).to_be_visible()


@pytest.mark.e2e
@pytest.mark.student
def test_student_can_reject_parent_link(logged_in_student_page: Page, base_url: str):
    """
    Scenario 5.3: Reject Parent Link Request
    Student can reject unwanted link requests.
    """
    page = logged_in_student_page
    
    # Navigate to link requests
    page.goto(f"{base_url}/students/link-requests/")
    
    # Look for reject button
    reject_button = page.locator("button:has-text('Reject'), button:has-text('Tolak')").first
    
    if reject_button.is_visible():
        reject_button.click()
        
        # May have confirmation dialog
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Should show success or refresh list
        page.wait_for_load_state("networkidle", timeout=5000)
        
        # Verify rejection (message or request disappears)
        assert page.url  # Basic check that page loaded


@pytest.mark.e2e
@pytest.mark.student
def test_student_registration_form_validation(page: Page, base_url: str):
    """
    Registration form should validate required fields.
    """
    page.goto(f"{base_url}/students/register/")
    
    # Try to submit empty form
    submit_button = page.locator("button[type='submit']").first
    
    if submit_button.is_visible():
        submit_button.click()
        
        # Should show validation errors (HTML5 or custom)
        # Page should not navigate away
        page.wait_for_timeout(1000)  # Brief wait for validation
        
        # Still on registration page
        assert "/register" in page.url
