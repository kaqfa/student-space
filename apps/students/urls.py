from django.urls import path
from .views import (
    # Registration
    StudentRegistrationView, 
    ParentRegistrationView,
    
    # Student views
    StudentDashboardView,
    LinkRequestListView,
    LinkRequestActionView,
    
    # Parent views
    ParentDashboardView,
    MyStudentsListView,
    StudentCreateByParentView,
    StudentLinkView,
    ParentStudentDetailView,
    SelectStudentForQuizView,
    StudentProfileUpdateView,
    
    # Deprecated
    StudentListView,
)

app_name = "students"

urlpatterns = [
    # ============================================================
    # PUBLIC REGISTRATION
    # ============================================================
    path("register/", StudentRegistrationView.as_view(), name="register"),
    path("register/parent/", ParentRegistrationView.as_view(), name="register_parent"),
    
    # ============================================================
    # STUDENT ROUTES (for users with role='student')
    # ============================================================
    path("dashboard/", StudentDashboardView.as_view(), name="dashboard"),
    path("link-requests/", LinkRequestListView.as_view(), name="link_requests"),
    path("link-requests/<int:pk>/action/", LinkRequestActionView.as_view(), name="link_request_action"),
    path("profile/edit/", StudentProfileUpdateView.as_view(), name="profile_edit"),
    
    # ============================================================
    # PARENT ROUTES (for users with role='parent')
    # ============================================================
    path("parent/dashboard/", ParentDashboardView.as_view(), name="parent_dashboard"),
    path("my-students/", MyStudentsListView.as_view(), name="my_students"),
    path("my-students/create/", StudentCreateByParentView.as_view(), name="create_student"),
    path("my-students/link/", StudentLinkView.as_view(), name="link_student"),
    path("my-students/<int:pk>/", ParentStudentDetailView.as_view(), name="parent_student_detail"),
    path("my-students/<int:pk>/edit/", StudentProfileUpdateView.as_view(), name="parent_student_edit"),
    path("my-students/select-for-quiz/", SelectStudentForQuizView.as_view(), name="select_for_quiz"),
    
    # ============================================================
    # DEPRECATED ROUTES (using old Student model)
    # These routes are kept for backward compatibility
    # ============================================================
    path("list/", StudentListView.as_view(), name="list"),
]
