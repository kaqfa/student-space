from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("questions/", include("apps.questions.urls")),
    path("students/", include("apps.students.urls")),
    path("quizzes/", include("apps.quizzes.urls")),
    path("analytics/", include("apps.analytics.urls")),
    # Placeholder root - will redirect to generic view or simple home template
    # For now, let's redirect root to login or dashboard
    path("", include("apps.core.urls")), # Assuming core will handle home
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Serve static from STATIC_ROOT if collected
    # Also need to ensure we can serve directly from STATICFILES_DIRS if runserver is picky, 
    # but 'static()' helper usually falls back to finders if document_root is not passed.
    # However, standard practice for runserver is that it automagically works. 
    # Let's try adding explicit static serving mapping to STATICFILES_DIRS elements ?
    # No, 'static' helper serves from document_root.
    
    # Try just adding this line is usually enough if collectstatic was run:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # BUT wait, runserver serves from STATICFILES_DIRS by default. 
    # If we ran collectstatic, we have files in STATIC_ROOT.
    # It shouldn't hurt to serve both or just rely on runserver logic which looks at STATICFILES_DIRS.
    
    # Let's stick to standard practice:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
