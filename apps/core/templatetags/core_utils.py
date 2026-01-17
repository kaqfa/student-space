from django import template

register = template.Library()

@register.filter
def to_char(value):
    try:
        return chr(65 + int(value))
    except (ValueError, TypeError):
        return ""

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    if dictionary is None:
        return None
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None
