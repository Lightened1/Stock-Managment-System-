from django.apps import AppConfig



class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

from django import template

register = template.Library()

@register.filter
def break_loop(value, index):
    return value[:index]



