from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def admin_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for views that checks that the user is an admin.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_superuser or u.role == "admin"),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def parent_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for views that checks that the user is a parent.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == "parent",
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def parent_or_admin_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for views that checks that the user is a parent or admin.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_superuser or u.role in ["admin", "parent"]),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def student_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator for views that checks that the user is a student.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role == "student",
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


# Backward compatibility aliases
def pengajar_or_admin_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Deprecated: Use parent_or_admin_required instead.
    Kept for backward compatibility.
    """
    return parent_or_admin_required(function, redirect_field_name, login_url)


def student_only(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Deprecated: Use student_required instead.
    Kept for backward compatibility.
    """
    return student_required(function, redirect_field_name, login_url)
