from django import template
from django.utils.html import strip_tags
import html

register = template.Library()


@register.filter(name='clean_excerpt')
def clean_excerpt(value, word_count=30):
    """
    Strip HTML tags and decode HTML entities for clean excerpts.
    Usage: {{ post.content|clean_excerpt:30 }}
    """
    if not value:
        return ''
    
    # First decode HTML entities (&nbsp; -> space, &amp; -> &, etc.)
    decoded = html.unescape(str(value))
    
    # Then strip HTML tags
    stripped = strip_tags(decoded)
    
    # Clean up extra whitespace
    cleaned = ' '.join(stripped.split())
    
    # Truncate to word count
    words = cleaned.split()
    if len(words) > word_count:
        return ' '.join(words[:word_count]) + '...'
    
    return cleaned
