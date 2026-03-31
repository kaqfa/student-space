from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import ProfileView

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("password-change/", auth_views.PasswordChangeView.as_view(template_name="accounts/password_change.html", success_url=reverse_lazy("profile")), name="password_change"),
]
