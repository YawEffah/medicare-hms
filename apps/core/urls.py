from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Patients
    path('patients/', views.patient_list_view, name='patient_list'),
    path('patients/add/', views.patient_create_view, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail_view, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_update_view, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete_view, name='patient_delete'),

    # Appointments
    path('appointments/', views.appointment_list_view, name='appointment_list'),
    path('appointments/add/', views.appointment_create_view, name='appointment_create'),
    path('appointments/<int:pk>/', views.appointment_detail_view, name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.appointment_update_view, name='appointment_update'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel_view, name='appointment_cancel'),
    path('appointments/today/', views.appointment_today_view, name='appointment_today'),

    # Medical Records
    path('records/', views.record_list_view, name='record_list'),
    path('records/add/', views.record_create_view, name='record_create'),
    path('records/<int:pk>/', views.record_detail_view, name='record_detail'),
    path('records/<int:pk>/edit/', views.record_update_view, name='record_update'),
    path('records/patient/<int:patient_pk>/history/', views.patient_history_view, name='patient_history'),

    # Analytics & Reports
    path('reports/', views.reports_dashboard_view, name='reports_dashboard'),
    path('reports/daily/', views.daily_report_view, name='daily_report'),

    # Public & Patient Portal
    path('', views.landing_view, name='landing'),
    path('portal/dashboard/', views.patient_dashboard_view, name='patient_dashboard'),
    path('portal/book/', views.patient_book_appointment_view, name='patient_book_appointment'),

    # Notifications API
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/<int:pk>/read/', views.api_mark_notification_read, name='api_mark_notification_read'),
]
