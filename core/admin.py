from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Hospital, Doctor, Patient, Appointment, LabReport, Reminder

class HospitalInline(admin.StackedInline):
    model = Hospital
    can_delete = False
    verbose_name_plural = 'Hospital Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (HospitalInline, )
    fieldsets = UserAdmin.fieldsets + (
        ('Roles', {'fields': ('is_hospital_admin', 'is_doctor', 'is_patient', 'is_lab', 'is_staff_member')}),
    )
    list_display = ['username', 'email', 'is_hospital_admin', 'is_doctor', 'get_hospital_name']
    
    def get_hospital_name(self, obj):
        if hasattr(obj, 'hospital_profile'):
            return obj.hospital_profile.name
        return '-'
    get_hospital_name.short_description = 'Hospital'

# admin.site.unregister(User) # Unregister original User

from django import forms

class HospitalCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, help_text="Required. 150 characters or fewer.")
    password = forms.CharField(widget=forms.PasswordInput, help_text="Enter a strong password.")

    class Meta:
        model = Hospital
        fields = ['username', 'password', 'name', 'address', 'allowed_ip_address']

class HospitalAdmin(admin.ModelAdmin):
    form = HospitalCreationForm
    list_display = ['name', 'address', 'get_username']
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new hospital
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Create the user first
            user = User.objects.create_user(username=username, password=password)
            user.is_hospital_admin = True
            user.save()
            
            # Link user to hospital
            obj.user = user
        else:
            # If editing, we don't update username/password here to avoid confusion
            # You can handle updates if needed, but usually we just save the hospital info
            pass
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        # If we are editing (obj is not None), maybe hide username/password or make them readonly
        # For now, we'll keep the custom form only for adding, but let's stick to simple logic
        if obj:
            self.form = forms.ModelForm # Fallback to default for editing? 
            # Or better, just exclude username/password in edit mode
            class HospitalChangeForm(forms.ModelForm):
                class Meta:
                    model = Hospital
                    exclude = ['user']
            kwargs['form'] = HospitalChangeForm
        return super().get_form(request, obj, **kwargs)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(LabReport)
admin.site.register(Reminder)
