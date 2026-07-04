import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def parse_medicines(value):
    """
    Parses medicine strings that might be in JSON format from older prescriptions
    or text format from newer ones.
    """
    if not value or value.strip() == "":
        return ""
        
    if value == "No Medicines Prescribed":
        return value

    try:
        # Try to parse as JSON first
        meds = json.loads(value)
        if isinstance(meds, list):
            result = ""
            for i, med in enumerate(meds, 1):
                name = med.get('name', 'Unknown')
                timing = med.get('timing', '')
                condition = med.get('condition', '')
                is_available = med.get('is_available', True)
                
                # Format similarly to the new text format
                result += f"{i}. <strong>{name}</strong>"
                if timing or condition:
                    result += " - "
                    if timing:
                        result += f"{timing}"
                    if condition:
                        result += f" ({condition})"
                
                if not is_available:
                    result += ' <span class="badge bg-danger ms-2" style="font-size: 0.75rem;"><i class="fas fa-exclamation-circle me-1"></i>Not available in Pharmacy - Buy from outside</span>'
                    
                result += "<br>"
            return mark_safe(result)
    except json.JSONDecodeError:
        # Not JSON, return as is (but replace newlines with <br> for HTML rendering)
        return mark_safe(value.replace('\n', '<br>'))
    
    return value
