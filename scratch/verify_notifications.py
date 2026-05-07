import os
import sys
import django
from unittest.mock import MagicMock

# Set up Django environment
sys.path.append(r'c:\Users\effah\OneDrive\Documents\Projects\medicare-hms')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_system.settings')
django.setup()

from apps.core.utils import (
    send_welcome_notification, 
    send_appointment_notification,
    send_appointment_update_notification,
    send_appointment_cancellation_notification,
    send_appointment_reminder
)
from apps.accounts.models import CustomUser
from apps.core.models import Patient, Appointment
from datetime import date, time

# Mock the sending functions to just print the messages
import apps.core.utils as utils
utils.send_email_notification = lambda email, subject, message: print(f"\n--- EMAIL ---\nTo: {email}\nSubject: {subject}\nMessage:\n{message}\n")
utils.send_sms_notification = lambda phone, message: print(f"--- SMS ---\nTo: {phone}\nMessage:\n{message}\n")

# Create mock objects
user = MagicMock(spec=CustomUser)
user.username = "jdoe"
user.email = "jdoe@example.com"
user.phone = "0240000000"
user.role = "patient"
user.get_full_name.return_value = "John Doe"

patient = MagicMock(spec=Patient)
patient.full_name = "Jane Smith"
patient.email = "jane@example.com"
patient.phone = "0550000000"

doctor = MagicMock(spec=CustomUser)
doctor.last_name = "Appiah"
doctor.email = "dr.appiah@medicare.com"
doctor.phone = "0200000000"
doctor.get_full_name.return_value = "Kwame Appiah"

appt = MagicMock(spec=Appointment)
appt.patient = patient
appt.doctor = doctor
appt.appointment_date = date(2026, 5, 8)
appt.appointment_time = time(10, 30)
appt.get_appointment_type_display.return_value = "General Consultation"
appt.get_status_display.return_value = "Scheduled"

print("=== TESTING WELCOME NOTIFICATION (PATIENT) ===")
send_welcome_notification(user)

user.role = "doctor"
user.get_role_display.return_value = "Medical Doctor"
print("=== TESTING WELCOME NOTIFICATION (STAFF) ===")
send_welcome_notification(user, password="TempPassword123")

print("=== TESTING APPOINTMENT CONFIRMATION ===")
send_appointment_notification(appt)

print("=== TESTING APPOINTMENT UPDATE ===")
send_appointment_update_notification(appt)

print("=== TESTING APPOINTMENT CANCELLATION ===")
send_appointment_cancellation_notification(appt)

print("=== TESTING APPOINTMENT REMINDER ===")
send_appointment_reminder(appt)
