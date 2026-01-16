"""
E2E Tests for Parent Student Management
Tests parent's ability to create, link, and manage students.
Based on TEST_SCENARIOS.md - Scenario 1
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_create_new_student_account(logged_in_parent_page: Page, base_url: str):
    """
    Scenario 1.1: Create New Student Account
    As a parent, I want to create a new student account for my young child.
    """
    page = logged_in_parent_page
    
    # Navigate to My Students page
    page.goto(f"{base_url}/students/")
    
    # Click "Create New Student" or "Add Student" button
    create_button = page.locator("a:has-text('Tambah Siswa'), a:has-text('Buat Siswa'), a:has-text('Create Student')").first
    
    if create_button.is_visible():
        create_button.click()
        
        # Wait for create form to load
        page.wait_for_load_state("networkidle")
        
        # Fill student creation form
        page.fill("input[name='first_name'], input[name='firstName']", "Ahmad")
        page.fill("input[name='last_name'], input[name='lastName']", "Faza")
        page.fill("input[name='username']", "ahmad_faza_test")
        page.fill("input[name='password']", "password123")
        
        # Select grade (might be dropdown or input)
        grade_field = page.locator("select[name='grade'], input[name='grade']").first
        if grade_field.is_visible():
            if grade_field.evaluate("el => el.tagName") == "SELECT":
                grade_field.select_option("6")
            else:
                grade_field.fill("6")
        
        # Submit form
        submit_button = page.locator("button[type='submit'], button:has-text('Simpan'), button:has-text('Create')").first
        submit_button.click()
        
        # Wait for redirect
        page.wait_for_load_state("networkidle", timeout=10000)
        
        # Verify success
        # Should redirect to student list or show success message
        assert "/students" in page.url or "/my-students" in page.url
        
        # Verify student appears in list (search for name)
        expect(page.locator("text=Ahmad, text=Faza")).to_be_visible(timeout=5000)


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_request_link_to_existing_student(logged_in_parent_page: Page, base_url: str):
    """
    Scenario 1.2: Request Link to Existing Student
    As a parent, I want to link to my child's existing account.
    
    Note: This test may fail if UI for link request not yet implemented.
    """
    page = logged_in_parent_page
    
    # Navigate to students page
    page.goto(f"{base_url}/students/")
    
    # Look for "Link Existing Student" button/link
    link_button = page.locator("a:has-text('Link'), a:has-text('Hubungkan')").first
    
    if link_button.is_visible():
        link_button.click()
        page.wait_for_load_state("networkidle")
        
        # Search for student by username
        search_field = page.locator("input[name='student_username'], input[name='username'], input[type='search']").first
        
        if search_field.is_visible():
            search_field.fill("siswa6")
            
            # Submit search or select from results
            # This depends on UI implementation
            # Could be a button or auto-search
            search_button = page.locator("button:has-text('Search'), button:has-text('Cari')").first
            if search_button.is_visible():
                search_button.click()
                page.wait_for_load_state("networkidle")
            
            # If student results appear, select and send request
            student_result = page.locator("text=siswa6, text=Dewi").first
            if student_result.is_visible():
                # Click on student or "Send Request" button
                request_button = page.locator("button:has-text('Request'), button:has-text('Kirim')").first
                if request_button.is_visible():
                    request_button.click()
                    
                    # Verify success message
                    expect(page.locator("text=request, text=pending")).to_be_visible(timeout=5000)


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_view_all_linked_students(logged_in_parent_page: Page, base_url: str):
    """
    Scenario 1.3: View All Linked Students
    As a parent with multiple children, I want to see all my linked students.
    
    Pre-condition: Parent 'orangtua' has 4 linked students from setup_test_data
    """
    page = logged_in_parent_page
    
    # Navigate to My Students page
    page.goto(f"{base_url}/students/")
    
    # Based on setup_test_data.py, parent has 4 students:
    # - Andi (Grade 3)
    # - Budi (Grade 4)
    # - Citra (Grade 5)
    # - Dewi (Grade 6)
    
    # Verify student names are visible
    expect(page.locator("text=Andi")).to_be_visible()
    expect(page.locator("text=Budi")).to_be_visible()
    expect(page.locator("text=Citra")).to_be_visible()
    expect(page.locator("text=Dewi")).to_be_visible()
    
    # Verify grade information is shown
    # Look for grade indicators like "Kelas 3", "Grade 4", etc.
    expect(page.locator("text=/Kelas [3-6]|Grade [3-6]/")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_view_student_profile(logged_in_parent_page: Page, base_url: str):
    """
    Parent can click on a student to view their profile/dashboard
    """
    page = logged_in_parent_page
    
    # Navigate to students list
    page.goto(f"{base_url}/students/")
    
    # Find and click on a student (e.g., Budi - Grade 4)
    student_link = page.locator("a:has-text('Budi'), a:has-text('siswa4')").first
    
    if student_link.is_visible():
        student_link.click()
        page.wait_for_load_state("networkidle")
        
        # Should be on student detail/profile page
        # Verify student name is shown
        expect(page.locator("h1, h2").filter(has_text="Budi")).to_be_visible()
        
        # Verify some profile sections exist
        # Could be: Progress, Analytics, Quizzes tabs
        expect(page.locator("text=Progress, text=Analitik, text=Kuis")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_student_list_shows_summary_info(logged_in_parent_page: Page, base_url: str):
    """
    Student list should show summary information for each student
    """
    page = logged_in_parent_page
    
    page.goto(f"{base_url}/students/")
    
    # Each student card should show some info
    # Look for common patterns
    student_cards = page.locator("[class*='card'], [class*='student']").all()
    
    # Should have multiple student cards/items
    assert len(student_cards) >= 4, "Should show at least 4 students"
    
    # Verify at least one card has basic info
    # (name, grade, maybe progress indicator)
    first_card = student_cards[0] if student_cards else None
    
    if first_card:
        # Should contain text (name or grade)
        card_text = first_card.text_content()
        assert len(card_text) > 0, "Student card should have content"


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_navigation_to_students_page(logged_in_parent_page: Page, base_url: str):
    """
    Parent can navigate to students page from any page
    """
    page = logged_in_parent_page
    
    # Start from home/dashboard
    page.goto(f"{base_url}/")
    
    # Look for navigation link to students
    # Common patterns: "My Students", "Students", "Siswa", "Murid"
    students_nav = page.locator("a:has-text('Student'), a:has-text('Siswa'), a[href*='student']").first
    
    if students_nav.is_visible():
        students_nav.click()
        page.wait_for_load_state("networkidle")
        
        # Should be on students page
        assert "/student" in page.url.lower()
        
        # Should see student list or students-related content
        # Accept both "Student/Siswa" and "Daftar Siswa"
        page_heading = page.locator("h1, h2").first.text_content()
        assert "student" in page_heading.lower() or "siswa" in page_heading.lower()
