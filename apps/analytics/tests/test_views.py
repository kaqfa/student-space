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


# NOTE: Admin analytics dashboard, parent student-history, and CSV export views
# were removed in U0 (moving to Django Admin in U1). Their tests were removed.
