
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EmergencyCase, StaffHealthStatus

@login_required
def resolve_emergency_case(request, case_id):
    if not (request.user.is_doctor or request.user.is_hospital_admin):
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard')
        
    case = get_object_or_404(EmergencyCase, id=case_id)
    
    case.status = 'Resolved'
    case.save()
    messages.success(request, f"Emergency Case '{case.patient_name}' marked as Resolved.")
        
    return redirect(request.META.get('HTTP_REFERER', 'hospital_emergency'))

@login_required
def delete_emergency_case(request, case_id):
    if not request.user.is_hospital_admin:
        messages.error(request, "Only admins can delete cases.")
        return redirect('dashboard')
        
    case = get_object_or_404(EmergencyCase, id=case_id)
    case.delete()
    messages.success(request, f"Emergency Case '{case.patient_name}' deleted.")
    return redirect(request.META.get('HTTP_REFERER', 'hospital_emergency'))


