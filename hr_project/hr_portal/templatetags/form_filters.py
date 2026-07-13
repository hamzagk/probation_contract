from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """Add a CSS class to a form field"""
    if hasattr(value, 'as_widget'):
        return value.as_widget(attrs={'class': arg})
    return value
