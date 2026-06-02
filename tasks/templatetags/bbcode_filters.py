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