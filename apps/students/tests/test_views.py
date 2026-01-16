"""
Unit tests for students app views.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestStudentDashboardView:
    """Test student dashboard"""
    
    def test_requires_authentication(self, client):
        """Test dashboard requires login"""
        url = reverse('students:dashboard')
        response = client.get(url)
        assert response.status_code == 302
        assert 'login' in response.url
    
    def test_student_can_access(self, client, student_user):
        """Test student can access their dashboard"""
        client.force_login(student_user)
        url = reverse('students:dashboard')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_parent_cannot_access(self, client, parent_user):
        """Test parent cannot access student dashboard"""
        client.force_login(parent_user)
        url = reverse('students:dashboard')
        response = client.get(url)
        # Should redirect or show 403
        assert response.status_code in [302, 403]


@pytest.mark.django_db
class TestParentDashboardView:
    """Test parent dashboard"""
    
    def test_requires_authentication(self, client):
        """Test dashboard requires login"""
        url = reverse('students:parent_dashboard')
        response = client.get(url)
        assert response.status_code == 302
    
    def test_parent_can_access(self, client, parent_user):
        """Test parent can access their dashboard"""
        client.force_login(parent_user)
        url = reverse('students:parent_dashboard')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_student_cannot_access(self, client, student_user):
        """Test student cannot access parent dashboard"""
        client.force_login(student_user)
        url = reverse('students:parent_dashboard')
        response = client.get(url)
        assert response.status_code in [302, 403]


@pytest.mark.django_db
class TestMyStudentsListView:
    """Test parent's students list"""
    
    def test_requires_parent_role(self, client, student_user):
        """Test requires parent role"""
        client.force_login(student_user)
        url = reverse('students:my_students')
        response = client.get(url)
        assert response.status_code in [302, 403]
    
    def test_parent_sees_linked_students(self, client, parent_user, parent_student_link):
        """Test parent sees their linked students"""
        client.force_login(parent_user)
        url = reverse('students:my_students')
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestLinkRequestViews:
    """Test link request approve/reject"""
    
    def test_link_action_requires_student(self, client, parent_user, parent_student_link):
        """Test only student can perform link actions"""
        client.force_login(parent_user)
        url = reverse('students:link_request_action', args=[parent_student_link.pk])
        response = client.post(url, {'action': 'approve'})
        assert response.status_code in [302, 403]
