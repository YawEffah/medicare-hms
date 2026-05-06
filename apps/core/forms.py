from django import forms
from .models import Patient, Appointment, MedicalRecord, VitalSign
from apps.accounts.models import CustomUser


class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )

    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'blood_group', 'phone', 'email', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'allergies', 'chronic_conditions',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'date_of_birth':
                field.widget.attrs['class'] = 'form-input'
            label = field.label or name.replace('_', ' ').capitalize()
            field.widget.attrs['placeholder'] = f"Enter {label.lower()}..."
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3


class PatientSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, ID or phone...',
            'class': 'form-input'
        })
    )


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'})
    )

    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'appointment_date', 'appointment_time',
            'appointment_type', 'status', 'reason', 'notes',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = CustomUser.objects.filter(role='doctor', is_active=True)
        for name, field in self.fields.items():
            if name not in ('appointment_date', 'appointment_time'):
                field.widget.attrs['class'] = 'form-input'
            label = field.label or name.replace('_', ' ').capitalize()
            field.widget.attrs['placeholder'] = f"Enter {label.lower()}..."
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3


class AppointmentFilterForm(forms.Form):
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
    status = forms.ChoiceField(required=False, choices=[('', 'All Statuses')] + Appointment.STATUS_CHOICES,
                               widget=forms.Select(attrs={'class': 'form-input'}))
    doctor = forms.ModelChoiceField(
        required=False,
        queryset=CustomUser.objects.filter(role='doctor'),
        empty_label='All Doctors',
        widget=forms.Select(attrs={'class': 'form-input'})
    )


class MedicalRecordForm(forms.ModelForm):
    visit_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
    follow_up_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))

    class Meta:
        model = MedicalRecord
        fields = [
            'patient', 'doctor', 'appointment', 'visit_date',
            'chief_complaint', 'diagnosis', 'treatment',
            'prescription', 'notes', 'follow_up_date',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = CustomUser.objects.filter(role='doctor', is_active=True)
        for name, field in self.fields.items():
            if name not in ('visit_date', 'follow_up_date'):
                field.widget.attrs['class'] = 'form-input'
            label = field.label or name.replace('_', ' ').capitalize()
            field.widget.attrs['placeholder'] = f"Enter {label.lower()}..."
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3


class VitalSignForm(forms.ModelForm):
    class Meta:
        model = VitalSign
        fields = [
            'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'pulse_rate', 'respiratory_rate', 'oxygen_saturation', 'weight', 'height',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            field.required = False
            label = field.label or name.replace('_', ' ').capitalize()
            field.widget.attrs['placeholder'] = f"Enter {label.lower()}..."
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3
