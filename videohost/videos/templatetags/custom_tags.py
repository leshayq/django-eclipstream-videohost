from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def lower(value):
    """Converts a string into all lowercase"""
    return value.lower()

@register.filter
def format_duration(value):
    start_seconds = int(value)
    minutes = start_seconds // 60
    seconds = start_seconds % 60
    if seconds < 10:
        duration = f'{minutes}:{str(seconds).zfill(2)}'
        return duration
    else:
        duration = f'{minutes}:{seconds}'
        return duration