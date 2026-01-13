from .base import *

# Production settings
DEBUG = False
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Security settings
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Database for production (enforce POSTGRES usually, but keep flexible)
if env.str("DATABASE_ENGINE", default="sqlite3") == "postgresql":
    DATABASES["default"] = env.db()

# Static files
STATIC_ROOT = env("STATIC_ROOT", default=str(BASE_DIR / "staticfiles"))
