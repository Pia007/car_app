from django import template

register = template.Library()

@register.filter(name='format_phone')
def format_phone(value):
    value = str(value)
    return f"{value[:3]}-{value[3:6]}-{value[6:]}"
