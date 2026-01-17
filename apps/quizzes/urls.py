from django.urls import path
from .views import (
    # Admin/Parent Quiz Management
    QuizListView, 
    QuizCreateView, 
    QuizDetailView, 
    QuizUpdateView, 
    QuizDeleteView,
    QuizQuestionAddView, 
    QuizQuestionRemoveView,
    
    # Student/Proxy Quiz Taking
    StudentQuizListView,
    QuizTakeView,
    QuizResultView,
    ProxyQuizSelectStudentView,
    
    # Dedicated Quiz Creation Views
    SubjectQuizCreateView,
    CustomQuizCreateView,
)
from .views_ajax import SaveAnswerView

app_name = "quizzes"

urlpatterns = [
    # ============================================================
    # DEDICATED QUIZ CREATION INTERFACES
    # ============================================================
    path("create/subject/", SubjectQuizCreateView.as_view(), name="create_subject_quiz"),
    path("create/custom/", CustomQuizCreateView.as_view(), name="create_custom_quiz"),
    
    # ============================================================
    # ADMIN/PARENT QUIZ MANAGEMENT
    # ============================================================
    path("", QuizListView.as_view(), name="list"),
    path("create/", QuizCreateView.as_view(), name="create"),
    path("<int:pk>/", QuizDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", QuizUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", QuizDeleteView.as_view(), name="delete"),
    path("<int:pk>/add-questions/", QuizQuestionAddView.as_view(), name="question-add"),
    path("<int:pk>/remove-question/<int:question_id>/", QuizQuestionRemoveView.as_view(), name="question-remove"),
    
    # ============================================================
    # STUDENT/PROXY QUIZ TAKING
    # ============================================================
    # Available quizzes list (for student or parent proxy)
    path("available/", StudentQuizListView.as_view(), name="student-list"),
    
    # Take a quiz (supports ?student_id=X&proxy=1 for parent proxy mode)
    path("<int:pk>/take/", QuizTakeView.as_view(), name="take_quiz"),
    
    # AJAX: Save individual answer (auto-save)
    path("save-answer/", SaveAnswerView.as_view(), name="save_answer"),
    
    # View quiz result (supports ?student_id=X&proxy=1 for parent proxy mode)
    path("<int:pk>/result/", QuizResultView.as_view(), name="result"),
    
    # Parent proxy mode - select student and show available quizzes
    path("proxy/select/", ProxyQuizSelectStudentView.as_view(), name="proxy_select"),
]
