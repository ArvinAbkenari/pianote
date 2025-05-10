from django import template
from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone

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

@register.filter
def persian_timesince(value):
    """
    Returns a Persian human-readable time difference (e.g., '۳۵ دقیقه پیش').
    Accepts datetime or ISO string.
    """
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except Exception:
            return ''
    now = timezone.now()
    # Convert both to naive UTC for correct subtraction
    if timezone.is_aware(value):
        value = value.astimezone(dt_timezone.utc).replace(tzinfo=None)
    if timezone.is_aware(now):
        now = now.astimezone(dt_timezone.utc).replace(tzinfo=None)
    diff = now - value
    seconds = int(diff.total_seconds())
    if seconds < 60:
        result = f'{to_persian_digits(seconds)} ثانیه پیش'
    elif seconds < 3600:
        minutes = seconds // 60
        result = f'{to_persian_digits(minutes)} دقیقه پیش'
    elif seconds < 86400:
        hours = seconds // 3600
        result = f'{to_persian_digits(hours)} ساعت پیش'
    elif seconds < 2592000:
        days = seconds // 86400
        result = f'{to_persian_digits(days)} روز پیش'
    else:
        months = seconds // 2592000
        result = f'{to_persian_digits(months)} ماه پیش'
    return result

register.filter('to_persian_digits', to_persian_digits)
register.filter('persian_timesince', persian_timesince)