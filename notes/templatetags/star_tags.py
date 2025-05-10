from django import template
register = template.Library()

@register.filter
def star_class(rate, index):
    rate = float(rate)
    if rate >= index:
        return "bi-star-fill"
    elif rate >= index - 0.5:
        return "bi-star-half"
    else:
        return "bi-star"
    
def to_persian_digits(value):
    persian_digits = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    return ''.join(persian_digits.get(char, char) for char in str(value))

register.filter('to_persian_digits', to_persian_digits)