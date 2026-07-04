import json
from django import template

register = template.Library()

@register.filter
def parse_json(value):
    if not value:
        return []
    text = value.strip()
    if text.startswith('[') and text.endswith(']'):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return None


@register.filter
def lookup(value, key):
    """Look up a dictionary value by key"""
    if isinstance(value, dict):
        return value.get(key)
    return None


# Ward Management Filters
@register.filter
def sum_beds(wards):
    """Sum total beds across all wards"""
    return sum(ward.total_beds for ward in wards)

@register.filter
def sum_occupied(wards):
    """Sum occupied beds across all wards"""
    return sum(ward.occupied_beds for ward in wards)

@register.filter
def sum_available(wards):
    """Sum available beds across all wards"""
    return sum(ward.available_beds for ward in wards)


# Medicine Management Filters
@register.filter
def in_stock_count(medicines):
    """Count medicines in stock"""
    return sum(1 for med in medicines if med.stock_quantity > 0)

@register.filter
def out_of_stock_count(medicines):
    """Count medicines out of stock"""
    return sum(1 for med in medicines if med.stock_quantity == 0)


# Billing Filters
@register.filter
def sum_paid(admissions):
    """Sum total paid amount across admissions"""
    return sum(ad.bill_paid for ad in admissions)
