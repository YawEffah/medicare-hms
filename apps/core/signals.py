from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Appointment, MedicalRecord, Notification

@receiver(post_save, sender=Appointment)
def notify_appointment_status(sender, instance, created, **kwargs):
    if created:
        # Initial appointment creation
        # Notify Patient
        if instance.patient.user:
            Notification.objects.create(
                recipient=instance.patient.user,
                title="New Appointment Scheduled",
                message=f"Your appointment for {instance.appointment_type} on {instance.appointment_date} has been scheduled.",
                category='appointment',
                link=reverse('core:patient_dashboard')
            )
        
        # Notify Doctor
        if instance.doctor:
            Notification.objects.create(
                recipient=instance.doctor,
                title="New Appointment Assigned",
                message=f"A new appointment has been scheduled with you for {instance.patient.full_name} on {instance.appointment_date} at {instance.appointment_time.strftime('%I:%M %p')}.",
                category='appointment',
                link=reverse('core:appointment_list')
            )
    else:
        # Status update - Notify Patient
        if instance.patient.user:
            Notification.objects.create(
                recipient=instance.patient.user,
                title="Appointment Update",
                message=f"Your appointment on {instance.appointment_date} status has been updated to {instance.get_status_display()}.",
                category='appointment',
                link=reverse('core:patient_dashboard')
            )

@receiver(post_save, sender=MedicalRecord)
def notify_new_record(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.patient.user,
            title="New Medical Record",
            message=f"A new medical record from your visit on {instance.visit_date} has been added to your profile.",
            category='record',
            link=reverse('accounts:profile')
        )
