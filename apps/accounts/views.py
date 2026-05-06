from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import admin_only, hospital_staff_required
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import date, timedelta

from .forms import LoginForm, StaffRegistrationForm, StaffUpdateForm, PatientRegistrationForm
from .models import CustomUser
from apps.core.models import Patient, Appointment
from apps.core.utils import send_welcome_notification


def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'patient':
            return redirect('core:patient_dashboard')
        return redirect('accounts:dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            if user.role == 'patient':
                return redirect('core:patient_dashboard')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:landing')

def patient_register_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'patient':
            return redirect('core:patient_dashboard')
        return redirect('accounts:dashboard')
    
    form = PatientRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        send_welcome_notification(user)
        messages.success(request, 'Registration successful! Welcome to your patient portal.')
        return redirect('core:patient_dashboard')
    return render(request, 'accounts/patient_register.html', {'form': form})


@login_required
@hospital_staff_required
def dashboard_view(request):
    today = date.today()
    user = request.user
    
    # Global stats (accessible by all staff, but filtered for doctors)
    total_patients = Patient.objects.count()
    total_doctors = CustomUser.objects.filter(role='doctor', is_active=True).count()
    
    if user.role == 'doctor':
        # Doctor-specific dashboard
        today_appointments = Appointment.objects.filter(doctor=user, appointment_date=today).count()
        pending_appointments = Appointment.objects.filter(doctor=user, status='scheduled').count()
        upcoming = Appointment.objects.filter(
            doctor=user,
            appointment_date__gte=today,
            status='scheduled'
        ).select_related('patient').order_by('appointment_date', 'appointment_time')[:5]
    else:
        # Admin/Nurse/Receptionist dashboard (global view)
        today_appointments = Appointment.objects.filter(appointment_date=today).count()
        pending_appointments = Appointment.objects.filter(status='scheduled').count()
        upcoming = Appointment.objects.filter(
            appointment_date__gte=today,
            status='scheduled'
        ).select_related('patient', 'doctor').order_by('appointment_date', 'appointment_time')[:5]

    recent_patients = Patient.objects.order_by('-created_at')[:5]

    context = {
        'total_patients': total_patients,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'total_doctors': total_doctors,
        'upcoming_appointments': upcoming,
        'recent_patients': recent_patients,
        'today': today,
    }
    return render(request, 'dashboard/dashboard.html', context)


def is_admin(user):
    return user.is_superuser or user.role == 'admin'

@login_required
@admin_only
def staff_list_view(request):
    staff = CustomUser.objects.all().order_by('role', 'last_name')
    return render(request, 'accounts/staff_list.html', {'staff': staff})


@login_required
@admin_only
def staff_create_view(request):
    form = StaffRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        password = form.cleaned_data.get('password1')
        send_welcome_notification(user, password=password)
        messages.success(request, 'Staff member created successfully.')
        return redirect('accounts:staff_list')
    return render(request, 'accounts/staff_form.html', {'form': form, 'title': 'Add Staff'})


@login_required
@admin_only
def staff_update_view(request, pk):
    staff = get_object_or_404(CustomUser, pk=pk)
    form = StaffUpdateForm(request.POST or None, request.FILES or None, instance=staff)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Staff member updated successfully.')
        return redirect('accounts:staff_list')
    return render(request, 'accounts/staff_form.html', {'form': form, 'title': 'Edit Staff', 'staff': staff})


@login_required
@admin_only
def staff_delete_view(request, pk):
    staff = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff member removed.')
        return redirect('accounts:staff_list')
    return render(request, 'accounts/staff_confirm_delete.html', {'staff': staff})


@login_required
def profile_view(request):
    form = StaffUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})
