from django import template

register = template.Library()

@register.filter(name='format_phone')
def format_phone(value):
    """
    A custom Django template filter to format a numeric phone number as xxx-xxx-xxxx.

    This filter takes a numeric phone number as input and formats it into a standard
    xxx-xxx-xxxx format for display in templates.

    Args:
        value (int or str): The numeric phone number to be formatted.

    Returns:
        str: The formatted phone number in xxx-xxx-xxxx format.

    Usage in Templates:
        {{ phone_number|format_phone }}

    Example:
        Input: 1234567890
        Output: 123-456-7890
    """
    
    value = str(value) # Ensure the input is converted to a string for consistent handling
    return f"{value[:3]}-{value[3:6]}-{value[6:]}" # Format the phone number as xxx-xxx-xxxx
