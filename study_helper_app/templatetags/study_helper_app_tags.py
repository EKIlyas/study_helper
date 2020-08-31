import datetime

from django import template
from ..models import Cart

register = template.Library()


@register.simple_tag
def carts_today_count(user=None):
    return Cart.to_practice.get_queryset(user=user).count()
