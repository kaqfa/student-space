from django.urls import path
from .views import (
    QuestionCreateView,
    QuestionDeleteView,
    QuestionDetailView,
    QuestionListView,
    QuestionUpdateView,
    QuestionImportView,
    TagListView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView,
    KDListView,
    KDCreateView,
    KDUpdateView,
    KDDeleteView,
)

app_name = "questions"

urlpatterns = [
    path("", QuestionListView.as_view(), name="list"),
    path("create/", QuestionCreateView.as_view(), name="create"),
    path("import/", QuestionImportView.as_view(), name="import"),
    
    # Tag URLs
    path("tags/", TagListView.as_view(), name="tag-list"),
    path("tags/create/", TagCreateView.as_view(), name="tag-create"),
    path("tags/<int:pk>/update/", TagUpdateView.as_view(), name="tag-update"),
    path("tags/<int:pk>/delete/", TagDeleteView.as_view(), name="tag-delete"),

    # KD URLs
    path("kds/", KDListView.as_view(), name="kd-list"),
    path("kds/create/", KDCreateView.as_view(), name="kd-create"),
    path("kds/<int:pk>/update/", KDUpdateView.as_view(), name="kd-update"),
    path("kds/<int:pk>/delete/", KDDeleteView.as_view(), name="kd-delete"),
    
    # Detail paths need to be at the bottom to avoid conflict if I used slug (but here it's int:pk so it's fine, but good practice)
    path("<int:pk>/", QuestionDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", QuestionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", QuestionDeleteView.as_view(), name="delete"),
]
