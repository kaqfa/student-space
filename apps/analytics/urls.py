from django.urls import path
from .views import (
    StudentProgressView,
    AccuracyTrendAPIView,
)

app_name = "analytics"

urlpatterns = [
    # Student views
    path("progress/", StudentProgressView.as_view(), name="progress"),

    # API (powers student progress charts)
    path("api/accuracy-trend/", AccuracyTrendAPIView.as_view(), name="api-accuracy-trend"),
]
