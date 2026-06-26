from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, View
from django.shortcuts import redirect

User = get_user_model()


class HomeView(TemplateView):
    template_name = "core/home.html"


# NOTE: There is no custom admin dashboard anymore (U0). Admins use Django Admin.


class DashboardView(LoginRequiredMixin, View):
    """
    Main dashboard router that redirects to role-specific dashboards.
    """
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Student -> Student Dashboard
        if user.role == User.Role.STUDENT:
            return redirect('students:dashboard')
        
        # Parent -> Parent Dashboard
        if user.role == User.Role.PARENT:
            return redirect('students:parent_dashboard')
        
        # Admin / any other role -> Django Admin (all admin features live there)
        return redirect('/admin/')
