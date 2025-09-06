
from django import template

register = template.Library()
@register.filter
def three_comma(value):
    try:
        return "{:,}".format(int(value))
    except Exception:
        return value
    
    
@register.filter
def to_persian_digits(value):
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    return ''.join(persian_digits[int(ch)] if ch.isdigit() else ch for ch in str(value))