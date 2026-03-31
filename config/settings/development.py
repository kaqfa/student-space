from .base import *

# Development settings
DEBUG = True
SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-key")
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# Debug Toolbar
INSTALLED_APPS += ["debug_toolbar", "django_extensions"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

INTERNAL_IPS = ["127.0.0.1"]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
