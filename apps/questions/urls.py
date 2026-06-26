from django.urls import path

app_name = "questions"

# Custom admin UI (question/tag/KD CRUD + import) was removed in U0.
# These functions are now served exclusively via Django Admin (/admin/).
urlpatterns = []
