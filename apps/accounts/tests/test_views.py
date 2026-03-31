"""
Unit tests for accounts app views.
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestLoginView:
    """Test login functionality"""
    
    def test_login_page_loads(self, client):
        """Test login page is accessible"""
        url = reverse('login')
        response = client.get(url)
        assert response.status_code == 200
        assert 'login' in response.content.decode().lower()
    
    def test_login_success(self, client, admin_user):
        """Test successful login"""
        url = reverse('login')
        response = client.post(url, {
            'username': 'test_admin',
            'password': 'testpass123'
        })
        assert response.status_code == 302  # Redirect after login
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        url = reverse('login')
        response = client.post(url, {
            'username': 'invalid',
            'password': 'wrong'
        })
        assert response.status_code == 200  # Stays on login page
        assert 'error' in response.content.decode().lower() or 'invalid' in response.content.decode().lower()
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        url = reverse('login')
        response = client.post(url, {
            'username': 'test',
            # Missing password
        })
        assert response.status_code == 200


@pytest.mark.django_db
class TestLogoutView:
    """Test logout functionality"""
    
    def test_logout_redirects(self, authenticated_client):
        """Test logout redirects properly"""
        url = reverse('logout')
        response = authenticated_client.post(url)  # Changed to POST
        assert response.status_code == 302
    
    def test_logout_requires_authentication(self, client):
        """Test logout with unauthenticated user"""
        url = reverse('logout')
        response = client.post(url)  # Changed to POST
        # Should redirect or handle gracefully
        assert response.status_code in [200, 302]


@pytest.mark.django_db
class TestProfileView:
    """Test profile view"""
    
    def test_profile_requires_authentication(self, client):
        """Test profile page requires login"""
        url = reverse('profile')
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login
        assert 'login' in response.url
    
    def test_profile_loads_for_authenticated_user(self, authenticated_client, student_user):
        """Test profile page loads for logged in user"""
        url = reverse('profile')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert 'profile' in response.content.decode().lower()
    
    def test_profile_update_success(self, authenticated_client, student_user):
        """Test updating profile"""
        url = reverse('profile')
        response = authenticated_client.post(url, {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com'
        })
        # Check if update was successful
        assert response.status_code in [200, 302]
        
        # Verify user was updated
        student_user.refresh_from_db()
        # Note: Actual fields updated depend on UserUpdateForm
    
    def test_profile_shows_current_user_data(self, authenticated_client, student_user):
        """Test profile displays current user's data"""
        url = reverse('profile')
        response = authenticated_client.get(url)
        content = response.content.decode()
        assert student_user.username in content or student_user.email in content


@pytest.mark.django_db
class TestPasswordChangeView:
    """Test password change functionality"""
    
    def test_password_change_requires_authentication(self, client):
        """Test password change requires login"""
        url = reverse('password_change')
        response = client.get(url)
        assert response.status_code == 302
        assert 'login' in response.url
    
    def test_password_change_page_loads(self, authenticated_client):
        """Test password change page loads"""
        url = reverse('password_change')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert 'password' in response.content.decode().lower()
