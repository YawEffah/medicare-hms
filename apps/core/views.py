from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import (
    admin_only, doctor_required, clinical_staff_required, hospital_staff_required, role_required
)
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import date, timedelta, datetime

from .models import Patient, Appointment, MedicalRecord, VitalSign, Notification
from .forms import (
    PatientForm, PatientSearchForm, 
    AppointmentForm, AppointmentFilterForm,
    MedicalRecordForm, VitalSignForm
)
from .utils import (
    send_appointment_notification, 
    send_appointment_update_notification, 
    send_appointment_cancellation_notification
)
from apps.accounts.models import CustomUser


# --- Patient Views ---

@login_required
@hospital_staff_required
def patient_list_view(request):
    form = PatientSearchForm(request.GET or None)
    patients = Patient.objects.all()
    query = request.GET.get('query', '')
    if query:
        patients = patients.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(patient_id__icontains=query) |
            Q(phone__icontains=query)
        )
    return render(request, 'patients/patient_list.html', {
        'patients': patients,
        'form': form,
        'query': query,
    })


@login_required
@hospital_staff_required
def patient_create_view(request):
    form = PatientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        patient = form.save()
        messages.success(request, f'Patient {patient.full_name} registered successfully.')
        return redirect('core:patient_detail', pk=patient.pk)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Register Patient'})


@login_required
@hospital_staff_required
def patient_detail_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')[:10]
    records = MedicalRecord.objects.filter(patient=patient).order_by('-created_at')[:10]
    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'appointments': appointments,
        'records': records,
    })


@login_required
@hospital_staff_required
def patient_update_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Patient record updated.')
        return redirect('core:patient_detail', pk=patient.pk)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Edit Patient', 'patient': patient})


@login_required
@admin_only
def patient_delete_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'Patient record deleted.')
        return redirect('core:patient_list')
    return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})


# --- Appointment Views ---

@login_required
@hospital_staff_required
def appointment_list_view(request):
    appointments = Appointment.objects.select_related('patient', 'doctor').all()
    form = AppointmentFilterForm(request.GET or None)

    if form.is_valid():
        if form.cleaned_data.get('date_from'):
            appointments = appointments.filter(appointment_date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            appointments = appointments.filter(appointment_date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data.get('status'):
            appointments = appointments.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('doctor'):
            appointments = appointments.filter(doctor=form.cleaned_data['doctor'])

    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'form': form,
    })


@login_required
@hospital_staff_required
def appointment_create_view(request):
    initial = {}
    patient_id = request.GET.get('patient')
    if patient_id:
        initial['patient'] = patient_id

    form = AppointmentForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        appointment = form.save()
        send_appointment_notification(appointment)
        messages.success(request, 'Appointment scheduled successfully.')
        return redirect('core:appointment_detail', pk=appointment.pk)
    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Schedule Appointment'})


@login_required
@hospital_staff_required
def appointment_detail_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointments/appointment_detail.html', {'appointment': appointment})


@login_required
@hospital_staff_required
def appointment_update_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if request.method == 'POST' and form.is_valid():
        appointment = form.save()
        send_appointment_update_notification(appointment)
        messages.success(request, 'Appointment updated.')
        return redirect('core:appointment_detail', pk=appointment.pk)
    return render(request, 'appointments/appointment_form.html', {
        'form': form, 'title': 'Edit Appointment', 'appointment': appointment
    })


@login_required
@hospital_staff_required
def appointment_cancel_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        send_appointment_cancellation_notification(appointment)
        messages.warning(request, 'Appointment cancelled.')
        return redirect('core:appointment_list')
    return render(request, 'appointments/appointment_confirm_cancel.html', {'appointment': appointment})


@login_required
@hospital_staff_required
def appointment_today_view(request):
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        appointment_date=today
    ).select_related('patient', 'doctor').order_by('appointment_time')
    return render(request, 'appointments/appointment_today.html', {
        'appointments': appointments, 'today': today
    })


# --- Medical Record Views ---

@login_required
@clinical_staff_required
def record_list_view(request):
    records = MedicalRecord.objects.select_related('patient', 'doctor').all()
    patient_id = request.GET.get('patient')
    if patient_id:
        records = records.filter(patient_id=patient_id)
    return render(request, 'records/record_list.html', {'records': records})


@login_required
@doctor_required
def record_create_view(request):
    initial = {}
    patient_id = request.GET.get('patient')
    if patient_id:
        initial['patient'] = patient_id

    form = MedicalRecordForm(request.POST or None, initial=initial)
    vital_form = VitalSignForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        record = form.save()
        if any(request.POST.get(f) for f in vital_form.fields):
            if vital_form.is_valid():
                vital = vital_form.save(commit=False)
                vital.record = record
                vital.save()
        messages.success(request, 'Medical record created successfully.')
        return redirect('core:record_detail', pk=record.pk)

    return render(request, 'records/record_form.html', {
        'form': form,
        'vital_form': vital_form,
        'title': 'New Medical Record',
    })


@login_required
@clinical_staff_required
def record_detail_view(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    vitals = record.vitals.first()
    return render(request, 'records/record_detail.html', {'record': record, 'vitals': vitals})


@login_required
@doctor_required
def record_update_view(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    form = MedicalRecordForm(request.POST or None, instance=record)
    vital_form = VitalSignForm(request.POST or None, instance=record.vitals.first())

    if request.method == 'POST' and form.is_valid():
        form.save()
        if vital_form.is_valid():
            vital = vital_form.save(commit=False)
            vital.record = record
            vital.save()
        messages.success(request, 'Record updated.')
        return redirect('core:record_detail', pk=record.pk)

    return render(request, 'records/record_form.html', {
        'form': form, 'vital_form': vital_form, 'title': 'Edit Record', 'record': record
    })


@login_required
@clinical_staff_required
def patient_history_view(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk)
    records = MedicalRecord.objects.filter(patient=patient).prefetch_related('vitals')
    return render(request, 'records/patient_history.html', {'patient': patient, 'records': records})


# --- Analytics & Reports Views ---

@login_required
@role_required(['admin', 'doctor'])
def reports_dashboard_view(request):
    today = date.today()
    user = request.user
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Base querysets
    appts = Appointment.objects.all()
    patients_qs = Patient.objects.all()
    
    if user.role == 'doctor':
        appts = appts.filter(doctor=user)
        # For doctors, "their patients" are those they've had appointments with
        patients_qs = Patient.objects.filter(appointments__doctor=user).distinct()

    # Appointment stats
    appt_by_status = dict(
        appts.values('status').annotate(count=Count('id')).values_list('status', 'count')
    )
    appt_by_type = list(
        appts.values('appointment_type').annotate(count=Count('id'))
    )
    appt_this_week = appts.filter(appointment_date__gte=week_start).count()
    appt_this_month = appts.filter(appointment_date__gte=month_start).count()

    # Patients seen per month (last 6 months)
    monthly_patients = []
    for i in range(5, -1, -1):
        month = (today.replace(day=1) - timedelta(days=30 * i))
        # Use created_at for registration or appointment date for activity
        # Let's use registration for admin and first appointment for doctor?
        # Actually, let's stick to registrations for hospital-wide, 
        # and "new patients seen" for doctors.
        if user.role == 'doctor':
            count = Patient.objects.filter(
                appointments__doctor=user,
                appointments__appointment_date__year=month.year,
                appointments__appointment_date__month=month.month
            ).distinct().count()
        else:
            count = Patient.objects.filter(
                created_at__year=month.year,
                created_at__month=month.month
            ).count()
        monthly_patients.append({'month': month.strftime('%b %Y'), 'count': count})

    # Top doctors by appointments (only for Admins)
    top_doctors = None
    if user.role == 'admin' or user.is_superuser:
        top_doctors = CustomUser.objects.filter(role='doctor').annotate(
            appt_count=Count('appointments')
        ).order_by('-appt_count')[:5]

    context = {
        'appt_by_status': appt_by_status,
        'appt_by_type': appt_by_type,
        'appt_this_week': appt_this_week,
        'appt_this_month': appt_this_month,
        'monthly_patients': monthly_patients,
        'top_doctors': top_doctors,
        'total_patients': patients_qs.count(),
        'today': today,
        'is_doctor_report': user.role == 'doctor'
    }
    return render(request, 'reports/reports_dashboard.html', context)


@login_required
@role_required(['admin', 'doctor'])
def daily_report_view(request):
    report_date_str = request.GET.get('date')
    period = request.GET.get('period', 'day')
    user = request.user
    
    try:
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date() if report_date_str else date.today()
    except (ValueError, TypeError):
        report_date = date.today()

    # Calculate date range based on period
    start_date = report_date
    end_date = report_date
    period_label = report_date.strftime('%d %B %Y')

    if period == 'week':
        start_date = report_date - timedelta(days=report_date.weekday())
        end_date = start_date + timedelta(days=6)
        period_label = f"Week of {start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')}"
    elif period == 'month':
        start_date = report_date.replace(day=1)
        if report_date.month == 12:
            end_date = report_date.replace(year=report_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = report_date.replace(month=report_date.month + 1, day=1) - timedelta(days=1)
        period_label = report_date.strftime('%B %Y')

    appointments = Appointment.objects.filter(
        appointment_date__range=[start_date, end_date]
    ).select_related('patient', 'doctor').order_by('appointment_date', 'appointment_time')
    
    if user.role == 'doctor':
        appointments = appointments.filter(doctor=user)

    context = {
        'appointments': appointments,
        'report_date': report_date,
        'period': period,
        'period_label': period_label,
        'total': appointments.count(),
        'completed': appointments.filter(status='completed').count(),
        'cancelled': appointments.filter(status='cancelled').count(),
        'no_show': appointments.filter(status='no_show').count(),
        'is_doctor_report': user.role == 'doctor'
    }
    return render(request, 'reports/daily_report.html', context)


# --- Public & Patient Portal Views ---

def landing_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'patient':
            return redirect('core:patient_dashboard')
        return redirect('accounts:dashboard')
    return render(request, 'public/landing.html')


@login_required
def patient_dashboard_view(request):
    if request.user.role != 'patient':
        return redirect('accounts:dashboard')
        
    try:
        patient_profile = request.user.patient_profile
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('accounts:logout')

    upcoming_appointments = Appointment.objects.filter(
        patient=patient_profile,
        appointment_date__gte=date.today(),
        status='scheduled'
    ).order_by('appointment_date', 'appointment_time')

    past_appointments = Appointment.objects.filter(
        patient=patient_profile,
        appointment_date__lt=date.today()
    ).order_by('-appointment_date', '-appointment_time')[:5]

    context = {
        'patient': patient_profile,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    return render(request, 'portal/patient_dashboard.html', context)


@login_required
def patient_book_appointment_view(request):
    if request.user.role != 'patient':
        return redirect('accounts:dashboard')

    try:
        patient_profile = request.user.patient_profile
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('accounts:logout')

    form = AppointmentForm(request.POST or None, initial={'patient': patient_profile.pk})
    
    # Hide the patient field for patients booking their own appts
    form.fields['patient'].widget.attrs['class'] = 'hidden'
    form.fields['patient'].label = ''

    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = patient_profile # Enforce security
        appointment.save()
        send_appointment_notification(appointment)
        messages.success(request, 'Your appointment has been successfully scheduled!')
        return redirect('core:patient_dashboard')

    return render(request, 'portal/book_appointment.html', {'form': form})
from django.http import JsonResponse

# --- Notification Views ---

@login_required
def api_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)[:5]
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'category': n.category,
        'link': n.link,
        'created_at': n.created_at.strftime('%b %d, %H:%M')
    } for n in notifications]
    return JsonResponse({'notifications': data, 'count': request.user.notifications.filter(is_read=False).count()})

@login_required
def api_mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})
