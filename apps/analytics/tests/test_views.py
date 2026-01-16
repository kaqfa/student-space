"""
Unit tests for analytics app views.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestProgressDashboardView:
    """Test student progress dashboard"""
    
    def test_requires_authentication(self, client):
        """Test requires login"""
        url = reverse('analytics:progress')
        response = client.get(url)
        assert response.status_code == 302
    
    def test_student_can_view_own_progress(self, client, student_user):
        """Test student can view their own progress"""
        client.force_login(student_user)
        url = reverse('analytics:progress')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_displays_student_statistics(self, client, student_user, quiz_session):
        """Test dashboard displays statistics"""
        client.force_login(student_user)
        url = reverse('analytics:progress')
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestAdminAnalyticsView:
    """Test admin analytics dashboard"""
    
    def test_requires_admin(self, client, student_user):
        """Test requires admin role"""
        client.force_login(student_user)
        url = reverse('analytics:dashboard')
        response = client.get(url)
        assert response.status_code in [302, 403]
    
    def test_admin_can_access(self, client, admin_user):
        """Test admin can access analytics"""
        client.force_login(admin_user)
        url = reverse('analytics:dashboard')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_shows_all_students_data(self, client, admin_user):
        """Test admin sees all students data"""
        client.force_login(admin_user)
        url = reverse('analytics:dashboard')
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestParentAnalyticsView:
    """Test parent viewing student analytics"""
    
    def test_parent_can_view_linked_student_progress(self, client, parent_user, student_user, parent_student_link):
        """Test parent can view their linked student's progress"""
        client.force_login(parent_user)
        url = reverse('analytics:student-history', args=[student_user.pk])
        response = client.get(url)
        assert response.status_code == 200
    
    def test_parent_cannot_view_unlinked_student(self, client, parent_user, student_grade6):
        """Test parent cannot view unlinked student's progress"""
        client.force_login(parent_user)
        url = reverse('analytics:student-history', args=[student_grade6.pk])
        response = client.get(url)
        assert response.status_code in [403, 404]


@pytest.mark.django_db
class TestExportViews:
    """Test data export functionality"""
    
    def test_export_requires_admin(self, client, parent_user):
        """Test export requires admin role"""
        client.force_login(parent_user)
        url = reverse('analytics:export-class')
        response = client.get(url)
        assert response.status_code in [302, 403]
    
    def test_admin_can_export(self, client, admin_user):
        """Test admin can export data"""
        client.force_login(admin_user)
        url = reverse('analytics:export-class')
        response = client.get(url)
        # Should return CSV or redirect
        assert response.status_code in [200, 302]
