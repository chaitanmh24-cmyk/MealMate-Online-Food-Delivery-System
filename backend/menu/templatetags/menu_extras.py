from django import template

register = template.Library()


@register.filter(name='split')
def split_filter(value, delimiter=','):
    """
    Split a string by the given delimiter.
    Usage: {{ "a,b,c"|split:"," }}  → ['a', 'b', 'c']
    """
    return [item.strip() for item in str(value).split(delimiter)]
