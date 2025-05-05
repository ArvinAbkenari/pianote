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