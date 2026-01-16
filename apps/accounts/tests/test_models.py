"""
Unit tests for accounts app models.
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.models import ParentStudent

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self):
        """Test creating a basic user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.role == User.Role.STUDENT  # Default role
    
    def test_user_roles(self):
        """Test user role creation"""
        admin = User.objects.create_user(
            username='admin', password='pass', role=User.Role.ADMIN
        )
        parent = User.objects.create_user(
            username='parent', password='pass', role=User.Role.PARENT
        )
        student = User.objects.create_user(
            username='student', password='pass', role=User.Role.STUDENT
        )
        
        assert admin.role == User.Role.ADMIN
        assert parent.role == User.Role.PARENT
        assert student.role == User.Role.STUDENT
    
    def test_is_admin_property(self, admin_user):
        """Test is_admin property"""
        assert admin_user.is_admin is True
        
    def test_is_parent_property(self, parent_user):
        """Test is_parent property"""
        assert parent_user.is_parent is True
        
    def test_is_student_property(self, student_user):
        """Test is_student property"""
        assert student_user.is_student is True
    
    def test_is_parent_or_admin(self, admin_user, parent_user, student_user):
        """Test is_parent_or_admin property"""
        assert admin_user.is_parent_or_admin is True
        assert parent_user.is_parent_or_admin is True
        assert student_user.is_parent_or_admin is False
    
    def test_student_grade_field(self):
        """Test student-specific grade field"""
        student = User.objects.create_user(
            username='student_g4',
            password='pass',
            role=User.Role.STUDENT,
            grade=4
        )
        assert student.grade == 4
    
    def test_user_str_representation(self, student_user):
        """Test __str__ method"""
        assert 'test_student' in str(student_user)
        assert 'Student' in str(student_user)
    
    def test_get_linked_students_for_parent(self, parent_user, student_user):
        """Test get_linked_students method"""
        # Create approved link
        ParentStudent.create_with_new_student(parent_user, student_user)
        
        linked_students = parent_user.get_linked_students()
        assert student_user in linked_students
        assert linked_students.count() == 1
    
    def test_get_linked_students_returns_empty_for_non_parent(self, student_user):
        """Test get_linked_students returns empty for non-parent"""
        linked = student_user.get_linked_students()
        assert linked.count() == 0
    
    def test_get_linked_parents_for_student(self, parent_user, student_user):
        """Test get_linked_parents method"""
        ParentStudent.create_with_new_student(parent_user, student_user)
        
        linked_parents = student_user.get_linked_parents()
        assert parent_user in linked_parents
        assert linked_parents.count() == 1


@pytest.mark.django_db
class TestParentStudentModel:
    """Test ParentStudent linking model"""
    
    def test_create_with_new_student(self, parent_user, student_user):
        """Test creating link when parent creates student"""
        link = ParentStudent.create_with_new_student(parent_user, student_user)
        
        assert link.parent == parent_user
        assert link.student == student_user
        assert link.status == ParentStudent.Status.APPROVED
        assert link.created_by_parent is True
        assert link.verified_at is not None
    
    def test_request_link(self, parent_user, student_user):
        """Test requesting link to existing student"""
        link = ParentStudent.request_link(
            parent_user, 
            student_user, 
            notes='My child'
        )
        
        assert link.parent == parent_user
        assert link.student == student_user
        assert link.status == ParentStudent.Status.PENDING
        assert link.created_by_parent is False
        assert link.notes == 'My child'
        assert link.verified_at is None
    
    def test_approve_link(self, parent_user, student_user):
        """Test approving a pending link"""
        link = ParentStudent.request_link(parent_user, student_user)
        assert link.status == ParentStudent.Status.PENDING
        
        link.approve()
        
        assert link.status == ParentStudent.Status.APPROVED
        assert link.verified_at is not None
    
    def test_reject_link(self, parent_user, student_user):
        """Test rejecting a pending link"""
        link = ParentStudent.request_link(parent_user, student_user)
        
        link.reject()
        
        assert link.status == ParentStudent.Status.REJECTED
        assert link.verified_at is not None
    
    def test_unique_together_constraint(self, parent_user, student_user):
        """Test that same parent-student pair cannot be linked twice"""
        ParentStudent.create_with_new_student(parent_user, student_user)
        
        with pytest.raises(Exception):  # IntegrityError
            ParentStudent.create_with_new_student(parent_user, student_user)
    
    def test_str_representation(self, parent_student_link):
        """Test __str__ method"""
        str_repr = str(parent_student_link)
        assert 'Parent' in str_repr or 'test_parent' in str_repr
        assert 'Student' in str_repr or 'test_student' in str_repr
