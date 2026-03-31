"""
Unit tests for questions app views.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestQuestionListView:
    """Test question list view"""
    
    def test_requires_authentication(self, client):
        """Test requires login"""
        url = reverse('questions:list')
        response = client.get(url)
        assert response.status_code == 302
    
    def test_admin_can_access(self, client, admin_user):
        """Test admin can access question list"""
        client.force_login(admin_user)
        url = reverse('questions:list')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_parent_can_access(self, client, parent_user):
        """Test parent can access question list"""
        client.force_login(parent_user)
        url = reverse('questions:list')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_student_cannot_access(self, client, student_user):
        """Test student cannot access question list"""
        client.force_login(student_user)
        url = reverse('questions:list')
        response = client.get(url)
        assert response.status_code in [302, 403]


@pytest.mark.django_db
class TestQuestionCreateView:
    """Test question create view"""
    
    def test_requires_admin_or_parent(self, client, student_user):
        """Test students cannot create questions"""
        client.force_login(student_user)
        url = reverse('questions:create')
        response = client.get(url)
        assert response.status_code in [302, 403]
    
    def test_admin_can_create(self, client, admin_user):
        """Test admin can create questions"""
        client.force_login(admin_user)
        url = reverse('questions:create')
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestQuestionDetailView:
    """Test question detail view"""
    
    def test_view_question_detail(self, client, admin_user, question):
        """Test viewing question detail"""
        client.force_login(admin_user)
        url = reverse('questions:detail', args=[question.pk])
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestQuestionUpdateView:
    """Test question update view"""
    
    def test_admin_can_update(self, client, admin_user, question):
        """Test admin can update question"""
        client.force_login(admin_user)
        url = reverse('questions:update', args=[question.pk])
        response = client.get(url)
        assert response.status_code == 200
    
    def test_student_cannot_update(self, client, student_user, question):
        """Test student cannot update question"""
        client.force_login(student_user)
        url = reverse('questions:update', args=[question.pk])
        response = client.get(url)
        assert response.status_code in [302, 403]


@pytest.mark.django_db
class TestQuestionDeleteView:
    """Test question delete view"""
    
    def test_admin_can_delete(self, client, admin_user, question):
        """Test admin can delete question"""
        client.force_login(admin_user)
        url = reverse('questions:delete', args=[question.pk])
        response = client.post(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestQuestionImportView:
    """Test question import view"""
    
    def test_requires_admin_or_parent(self, client, student_user):
        """Test import requires admin or parent"""
        client.force_login(student_user)
        url = reverse('questions:import')
        response = client.get(url)
        assert response.status_code in [302, 403]
    
    def test_admin_can_access_import(self, client, admin_user):
        """Test admin can access import page"""
        client.force_login(admin_user)
        url = reverse('questions:import')
        response = client.get(url)
        assert response.status_code == 200
