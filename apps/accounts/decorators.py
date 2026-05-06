from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles):
    """
    Decorator for views that checks whether a user has a specific role.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.is_superuser or request.user.role == 'admin' or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "You do not have permission to access this page.")
            return redirect('accounts:dashboard')
        return _wrapped_view
    return decorator

# Specific decorators
def admin_only(view_func):
    return role_required(['admin'])(view_func)

def doctor_required(view_func):
    return role_required(['doctor'])(view_func)

def nurse_required(view_func):
    return role_required(['nurse'])(view_func)

def receptionist_required(view_func):
    return role_required(['receptionist'])(view_func)

def clinical_staff_required(view_func):
    """Doctors, Nurses, and Admins can access clinical data."""
    return role_required(['doctor', 'nurse'])(view_func)

def hospital_staff_required(view_func):
    """Any staff member (Admin, Doctor, Nurse, Receptionist)."""
    return role_required(['admin', 'doctor', 'nurse', 'receptionist'])(view_func)
