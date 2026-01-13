from django import template

register = template.Library()

@register.filter
def to_char(value):
    try:
        return chr(65 + int(value))
    except (ValueError, TypeError):
        return ""
