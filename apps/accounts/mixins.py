from django.contrib.auth.mixins import UserPassesTestMixin


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be an admin."""
    
    def test_func(self):
        return self.request.user.is_active and (
            self.request.user.is_superuser or self.request.user.role == "admin"
        )


class ParentRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be a parent."""
    
    def test_func(self):
        return self.request.user.is_active and self.request.user.role == "parent"


class ParentOrAdminMixin(UserPassesTestMixin):
    """Mixin that requires user to be a parent or admin."""
    
    def test_func(self):
        return self.request.user.is_active and (
            self.request.user.is_superuser
            or self.request.user.role in ["admin", "parent"]
        )


class StudentRequiredMixin(UserPassesTestMixin):
    """Mixin that requires user to be a student."""
    
    def test_func(self):
        return self.request.user.is_active and self.request.user.role == "student"


# Backward compatibility aliases
class PengajarOrAdminMixin(ParentOrAdminMixin):
    """
    Deprecated: Use ParentOrAdminMixin instead.
    Kept for backward compatibility.
    """
    pass


class StudentOnlyMixin(StudentRequiredMixin):
    """
    Deprecated: Use StudentRequiredMixin instead.
    Kept for backward compatibility.
    """
    pass
