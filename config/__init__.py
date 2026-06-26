# Expose Celery app so `celery -A config worker` works.
# Guarded import: Celery package is optional (only needed when running workers).
try:
    from .celery import app as celery_app  # noqa: F401
    __all__ = ('celery_app',)
except ImportError:
    # celery not installed — normal during dev/test without Redis
    pass
