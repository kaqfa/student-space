from django.urls import path
from .views import (
    StudentProgressView,
    AdminAnalyticsDashboardView,
    StudentAttemptHistoryView,
    AccuracyTrendAPIView,
    TagAnalyticsView,
    KDCoverageView,
    ExportStudentReportView,
    ExportClassSummaryView,
)

app_name = "analytics"

urlpatterns = [
    # Student views
    path("progress/", StudentProgressView.as_view(), name="progress"),
    
    # Admin views
    path("dashboard/", AdminAnalyticsDashboardView.as_view(), name="dashboard"),
    path("tags/", TagAnalyticsView.as_view(), name="tag-heatmap"),
    path("kd-coverage/", KDCoverageView.as_view(), name="kd-coverage"),
    path("student/<int:pk>/history/", StudentAttemptHistoryView.as_view(), name="student-history"),
    
    # Export
    path("export/student/<int:pk>/", ExportStudentReportView.as_view(), name="export-student"),
    path("export/class/", ExportClassSummaryView.as_view(), name="export-class"),
    
    # API
    path("api/accuracy-trend/", AccuracyTrendAPIView.as_view(), name="api-accuracy-trend"),
]
