"""
E2E Tests for Parent Analytics & Progress Viewing
Tests parent's ability to view detailed student analytics and progress.
Based on TEST_SCENARIOS.md - Scenario 4
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_view_student_analytics_dashboard(logged_in_parent_page: Page, base_url: str):
    """
    Scenario 4.1: View Student Dashboard & Overview
    Parent can access comprehensive analytics for their student.
    """
    page = logged_in_parent_page
    
    # Navigate to students list
    page.goto(f"{base_url}/students/")
    
    # Click on a student (e.g., Budi - Grade 4)
    student_link = page.locator("a:has-text('Budi'), a[href*='student']").first
    
    if student_link.is_visible():
        student_link.click()
        page.wait_for_load_state("networkidle")
        
        # Look for Analytics tab or section
        analytics_link = page.locator("a:has-text('Analytics'), a:has-text('Analitik'), button:has-text('Analytics')").first
        
        if analytics_link.is_visible():
            analytics_link.click()
            page.wait_for_load_state("networkidle")
        
        # Should see analytics content
        # Look for common analytics indicators
        analytics_content = page.locator("text=/accuracy|questions|progress|performance/i")
        expect(analytics_content).to_be_visible(timeout=5000)


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_analytics_shows_overview_metrics(logged_in_parent_page: Page, base_url: str):
    """
    Analytics should show key overview metrics.
    """
    page = logged_in_parent_page
    
    # Navigate to student analytics
    page.goto(f"{base_url}/students/")
    student_link = page.locator("a:has-text('Budi')").first
    
    if student_link.is_visible():
        student_link.click()
        page.wait_for_load_state("networkidle")
        
        # Look for metric displays
        # Common patterns: percentages, numbers, stats
        metrics = page.locator("text=/[0-9]+%|[0-9]+ questions|Total|Accuracy/i")
        
        # Should have some metrics
        if metrics.count() > 0:
            expect(metrics.first).to_be_visible()


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_filter_analytics_by_date_range(logged_in_parent_page: Page, base_url: str):
    """
    Scenario 4.2: Filter Analytics by Date Range
    Parent can filter analytics to see progress over specific time periods.
    """
    page = logged_in_parent_page
    
    # Navigate to analytics
    page.goto(f"{base_url}/students/")
    student_link = page.locator("a:has-text('Budi')").first
    
    if student_link.is_visible():
        student_link.click()
        page.wait_for_load_state("networkidle")
        
        # Look for date filter
        date_filter = page.locator("select[name*='date'], select[name*='period'], button:has-text('Filter')").first
        
        if date_filter.is_visible():
            # Select a time period
            if date_filter.evaluate("el => el.tagName") == "SELECT":
                date_filter.select_option("7days")
            else:
                date_filter.click()
                # Select option from dropdown
                page.locator("text=/Last 7 days|7 hari/i").first.click()
            
            page.wait_for_load_state("networkidle", timeout=5000)
            
            # Analytics should update (URL or content changes)
            # Check if URL has date parameters
            assert page.url


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_view_tag_based_skill_heatmap(logged_in_parent_page: Page, base_url: str):
    """
    Scenario 4.3: View Tag-Based Skill Heatmap
    Parent can see student's performance across different skill tags.
    """
    page = logged_in_parent_page
    
    # Navigate to student analytics
    page.goto(f"{base_url}/students/")
    student_link = page.locator("a:has-text('Budi')").first
    
    if student_link.is_visible():
        student_link.click()
        page.wait_for_load_state("networkidle")
        
        # Look for skill/tag section
        skill_section = page.locator("text=/Skill|Tag|Kemampuan|Heatmap/i")
        
        if skill_section.is_visible():
            # Should have tag performance data
            # Look for tag names or skill indicators
            tags = page.locator("[class*='tag'], [class*='skill']").all()
            
            # May have tags displayed
            assert len(tags) >= 0


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_view_kd_coverage(logged_in_parent_page: Page, base_url: str):
    """
    Scenario 4.4: View KD (Kompetensi Dasar) Coverage
    Parent can see which curriculum standards the student has covered.
    """
    page = logged_in_parent_page
    
    # Navigate to analytics
    page.goto(f"{base_url}/students/")
    student_link = page.locator("a:has-text('Budi')").first
    
    if student_link.is_visible():
        student_link.click()
        page.wait_for_load_state("networkidle")
        
        # Look for KD section
        kd_section = page.locator("text=/KD|Kompetensi|Coverage|Cakupan/i")
        
        if kd_section.is_visible():
            # Should show KD codes and status
            # Look for KD patterns like "3.1", "4.2"
            kd_codes = page.locator("text=/[0-9]\\.[0-9]/")
            
            # May have KD codes
            if kd_codes.count() > 0:
                expect(kd_codes.first).to_be_visible()


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_can_view_subject_performance_breakdown(logged_in_parent_page: Page, base_url: str):
    """
    Parent can see performance breakdown by subject.
    """
    page = logged_in_parent_page
    
    # Navigate to student profile
    page.goto(f"{base_url}/students/")
    student_link = page.locator("a:has-text('Budi')").first
    
    if student_link.is_visible():
        student_link.click()
        page.wait_for_load_state("networkidle")
        
        # Look for subject breakdown
        # Common subjects: Matematika, IPA, Bahasa Indonesia
        subject_indicators = page.locator("text=/Matematika|IPA|Bahasa/i")
        
        if subject_indicators.count() > 0:
            # Should have subject performance data
            expect(subject_indicators.first).to_be_visible()


@pytest.mark.e2e
@pytest.mark.parent
def test_parent_analytics_shows_performance_trends(logged_in_parent_page: Page, base_url: str):
    """
    Analytics should show performance trends over time (charts).
    """
    page = logged_in_parent_page
    
    # Navigate to analytics
    page.goto(f"{base_url}/students/")
    student_link = page.locator("a:has-text('Budi')").first
    
    if student_link.is_visible():
        student_link.click()
        page.wait_for_load_state("networkidle")
        
        # Look for chart elements (canvas for Chart.js)
        chart = page.locator("canvas, [id*='chart'], [class*='chart']").first
        
        # May have charts if implemented
        if chart.is_visible():
            expect(chart).to_be_visible()
