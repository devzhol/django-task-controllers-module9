import bbcode
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def bbcode_to_html(value):

    parser = bbcode.Parser()

    return mark_safe(
        parser.format(value)
    )


@register.filter
def completed_status(value):
    """Return a human-readable status for completed boolean values."""
    if isinstance(value, bool):
        return '✅ Выполнено' if value else '❌ В процессе'
    return value


@register.filter
def half(value):
    """Trim a string to its first half."""
    if value is None:
        return ''
    text = str(value)
    half_length = len(text) // 2
    return text[:half_length]


@register.simple_tag
def split_to_list(value, separator=','):
    """Split a string by separator and return a list of parts."""
    if value is None:
        return []
    return [part.strip() for part in str(value).split(separator) if part.strip()]