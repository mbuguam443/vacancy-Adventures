from django import template

register = template.Library()

@register.filter
def get_attr(obj, field):
    if hasattr(obj, field):
        val = getattr(obj, field)
        if callable(val):
            return val()
        return val
    return ''
