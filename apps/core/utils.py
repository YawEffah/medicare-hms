import logging
import requests
import threading
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def run_async(func):
    """Decorator to run a function in a background thread."""
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
    return wrapper


def send_email_notification(to_email, subject, message):
    """Send an email notification."""
    if not to_email:
        return False
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        return False


def send_sms_notification(to_phone, message):
    """Send an SMS via Arkesel Gateway."""
    api_key = getattr(settings, 'ARKESEL_API_KEY', '')
    sender_id = getattr(settings, 'ARKESEL_SENDER_ID', 'MediCare')
    
    if not to_phone or not api_key:
        logger.warning("SMS not sent: Missing phone number or Arkesel API key.")
        return False

    phone = to_phone.strip().replace(' ', '').replace('+', '')
    if phone.startswith('0'):
        phone = '233' + phone[1:]
    elif not phone.startswith('233') and len(phone) == 9:
        phone = '233' + phone

    url = "https://sms.arkesel.com/api/v2/sms/send"
    payload = {
        "sender": sender_id,
        "message": message,
        "recipients": [phone],
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        if response.status_code == 200 or result.get('status') == 'success':
            return True
        else:
            logger.error(f"Arkesel SMS failed: {result}")
            return False
    except Exception as e:
        logger.error(f"Arkesel SMS exception: {e}")
        return False


@run_async
def send_welcome_notification(user, password=None):
    """Send a welcome notification to a new patient or staff member."""
    subject = "Welcome to MediCare HMS"
    
    if user.role == 'patient':
        message = (
            f"Dear {user.get_full_name() or user.username},\n\n"
            f"Welcome to MediCare! Your patient account has been successfully created.\n\n"
            f"You can now log in to our portal to book appointments and view your medical records.\n\n"
            f"Username: {user.username}\n\n"
            f"Regards,\nMediCare Management"
        )
        sms_message = f"Welcome to MediCare! Your patient account ({user.username}) is ready. Log in to book appointments."
    else:
        role_display = user.get_role_display() if hasattr(user, 'get_role_display') else user.role
        message = (
            f"Dear {user.get_full_name() or user.username},\n\n"
            f"An account has been created for you as a {role_display} at MediCare HMS.\n\n"
            f"Username: {user.username}\n"
        )
        if password:
            message += f"Temporary Password: {password}\n"
        
        message += "\nPlease log in and change your password immediately to secure your account.\n\nRegards,\nMediCare Administration"
        sms_message = f"Welcome to the team! Your MediCare HMS account ({user.username}) as {role_display} has been created."

    send_email_notification(user.email, subject, message)
    if user.phone:
        send_sms_notification(user.phone, sms_message)


@run_async
def send_appointment_notification(appointment):
    """Send appointment confirmation to both patient and doctor."""
    patient = appointment.patient
    doctor = appointment.doctor
    doctor_name = doctor.get_full_name() if doctor else 'your assigned doctor'

    # Notify Patient
    status_label = appointment.get_status_display()
    subject_p = f"Appointment {status_label}: {appointment.appointment_date.strftime('%d %b %Y')}"
    message_p = (
        f"Dear {patient.full_name},\n\n"
        f"Your appointment has been {status_label.lower()}. Here are the details:\n\n"
        f"Date: {appointment.appointment_date.strftime('%A, %d %B %Y')}\n"
        f"Time: {appointment.appointment_time.strftime('%I:%M %p')}\n"
        f"Doctor: Dr. {doctor_name}\n"
        f"Type: {appointment.get_appointment_type_display()}\n\n"
        f"Please arrive at least 15 minutes before your scheduled time.\n\n"
        f"Regards,\nMediCare Management"
    )
    send_email_notification(patient.email, subject_p, message_p)
    sms_p = f"Hi {patient.full_name}, your appointment with Dr. {doctor_name} is {status_label.lower()} for {appointment.appointment_date} at {appointment.appointment_time.strftime('%I:%M %p')}."
    send_sms_notification(patient.phone, sms_p)

    # Notify Doctor
    if doctor:
        subject_d = f"New Appointment: {patient.full_name} – {appointment.appointment_date}"
        message_d = (
            f"Dear Dr. {doctor.last_name},\n\n"
            f"A new appointment has been scheduled for you.\n\n"
            f"Patient: {patient.full_name}\n"
            f"Date: {appointment.appointment_date.strftime('%A, %d %B %Y')}\n"
            f"Time: {appointment.appointment_time.strftime('%I:%M %p')}\n"
            f"Type: {appointment.get_appointment_type_display()}\n\n"
            f"Regards,\nMediCare HMS"
        )
        send_email_notification(doctor.email, subject_d, message_d)
        if doctor.phone:
            sms_d = f"Alert: New appointment with {patient.full_name} on {appointment.appointment_date} at {appointment.appointment_time.strftime('%I:%M %p')}."
            send_sms_notification(doctor.phone, sms_d)


@run_async
def send_appointment_update_notification(appointment):
    """Send update notification to both patient and doctor."""
    patient = appointment.patient
    doctor = appointment.doctor
    doctor_name = doctor.get_full_name() if doctor else 'your doctor'

    # Notify Patient
    status_label = appointment.get_status_display()
    subject = f"Appointment Update: {status_label}"
    message = (
        f"Dear {patient.full_name},\n\n"
        f"Your appointment details have been updated. The current status is: {status_label}.\n\n"
        f"Schedule:\n"
        f"Date: {appointment.appointment_date.strftime('%A, %d %B %Y')}\n"
        f"Time: {appointment.appointment_time.strftime('%I:%M %p')}\n"
        f"Doctor: Dr. {doctor_name}\n\n"
        f"Regards,\nMediCare Management"
    )
    send_email_notification(patient.email, subject, message)
    sms_p = f"Hi {patient.full_name}, your appointment with Dr. {doctor_name} on {appointment.appointment_date} has been updated. Status: {status_label}."
    send_sms_notification(patient.phone, sms_p)

    # Notify Doctor
    if doctor:
        subject_d = f"Appointment Updated: {patient.full_name} – {appointment.appointment_date}"
        message_d = (
            f"Dear Dr. {doctor.last_name},\n\n"
            f"An appointment with {patient.full_name} has been updated.\n\n"
            f"New Date: {appointment.appointment_date.strftime('%A, %d %B %Y')}\n"
            f"New Time: {appointment.appointment_time.strftime('%I:%M %p')}\n\n"
            f"Regards,\nMediCare HMS"
        )
        send_email_notification(doctor.email, subject_d, message_d)
        if doctor.phone:
            sms_d = f"Update: Appointment with {patient.full_name} moved to {appointment.appointment_date} at {appointment.appointment_time.strftime('%I:%M %p')}."
            send_sms_notification(doctor.phone, sms_d)


@run_async
def send_appointment_cancellation_notification(appointment):
    """Send cancellation notification to both patient and doctor."""
    patient = appointment.patient
    doctor = appointment.doctor

    # Notify Patient
    subject = f"Appointment Cancelled: {appointment.appointment_date.strftime('%d %b %Y')}"
    message = (
        f"Dear {patient.full_name},\n\n"
        f"Your appointment scheduled for {appointment.appointment_date.strftime('%A, %d %B %Y')} has been cancelled.\n\n"
        f"If you did not request this or would like to reschedule, please contact us or visit your portal.\n\n"
        f"Regards,\nMediCare Management"
    )
    send_email_notification(patient.email, subject, message)
    sms_p = f"Hi {patient.full_name}, your appointment on {appointment.appointment_date} has been cancelled. Contact us to reschedule."
    send_sms_notification(patient.phone, sms_p)

    # Notify Doctor
    if doctor:
        subject_d = f"Cancelled Appointment: {patient.full_name} – {appointment.appointment_date}"
        message_d = (
            f"Dear Dr. {doctor.last_name},\n\n"
            f"Your appointment with {patient.full_name} on {appointment.appointment_date} has been cancelled.\n\n"
            f"Regards,\nMediCare HMS"
        )
        send_email_notification(doctor.email, subject_d, message_d)
        if doctor.phone:
            sms_d = f"Cancellation: Appointment with {patient.full_name} on {appointment.appointment_date} has been cancelled."
            send_sms_notification(doctor.phone, sms_d)


@run_async
def send_appointment_reminder(appointment):
    """Send reminder 24 hours before appointment."""
    patient = appointment.patient
    doctor = appointment.doctor
    doctor_name = doctor.get_full_name() if doctor else 'your doctor'

    subject = f"Reminder: Appointment Tomorrow – {appointment.appointment_date.strftime('%d %b %Y')}"
    message = (
        f"Dear {patient.full_name},\n\n"
        f"This is a friendly reminder of your appointment scheduled for tomorrow.\n\n"
        f"Date: {appointment.appointment_date.strftime('%A, %d %B %Y')}\n"
        f"Time: {appointment.appointment_time.strftime('%I:%M %p')}\n"
        f"Doctor: Dr. {doctor_name}\n\n"
        f"We look forward to seeing you! Please contact us if you need to reschedule.\n\n"
        f"Regards,\nMediCare Management"
    )

    send_email_notification(patient.email, subject, message)
    sms_msg = f"Friendly reminder: You have an appointment tomorrow at {appointment.appointment_time.strftime('%I:%M %p')} with Dr. {doctor_name}. Status: {appointment.get_status_display()}."
    send_sms_notification(patient.phone, sms_msg)
    
    if doctor and doctor.phone:
        sms_d = f"Reminder: You have an appointment tomorrow with {patient.full_name} at {appointment.appointment_time.strftime('%I:%M %p')}."
        send_sms_notification(doctor.phone, sms_d)
