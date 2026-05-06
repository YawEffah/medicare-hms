from django.contrib import admin
from .models import Patient, Appointment, MedicalRecord, VitalSign


# ─── Inline: VitalSign inside MedicalRecord ───────────────────────────────────
class VitalSignInline(admin.StackedInline):
    model = VitalSign
    extra = 0
    max_num = 1
    can_delete = True
    verbose_name = "Vital Signs"
    verbose_name_plural = "Vital Signs"
    fieldsets = (
        ('Cardiovascular', {
            'fields': (('blood_pressure_systolic', 'blood_pressure_diastolic'), 'pulse_rate'),
        }),
        ('Respiratory & Temperature', {
            'fields': ('temperature', 'respiratory_rate', 'oxygen_saturation'),
        }),
        ('Body Metrics', {
            'fields': (('weight', 'height'),),
        }),
    )


# ─── Inline: Appointments inside Patient ──────────────────────────────────────
class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    show_change_link = True
    fields = ('appointment_date', 'appointment_time', 'doctor', 'appointment_type', 'status')
    readonly_fields = ('appointment_date', 'appointment_time', 'doctor', 'appointment_type', 'status')
    can_delete = False
    verbose_name = "Appointment"
    verbose_name_plural = "Recent Appointments"
    ordering = ('-appointment_date',)
    max_num = 5


# ─── Inline: Medical Records inside Patient ───────────────────────────────────
class MedicalRecordInline(admin.TabularInline):
    model = MedicalRecord
    extra = 0
    show_change_link = True
    fields = ('visit_date', 'doctor', 'chief_complaint', 'follow_up_date')
    readonly_fields = ('visit_date', 'doctor', 'chief_complaint', 'follow_up_date')
    can_delete = False
    verbose_name = "Medical Record"
    verbose_name_plural = "Medical Records"
    ordering = ('-visit_date',)
    max_num = 10


# ─── Patient Admin ─────────────────────────────────────────────────────────────
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'full_name', 'gender', 'blood_group', 'phone', 'email', 'age', 'created_at')
    list_display_links = ('patient_id', 'full_name')
    search_fields = ('first_name', 'last_name', 'patient_id', 'phone', 'email')
    list_filter = ('gender', 'blood_group')
    ordering = ('-created_at',)
    readonly_fields = ('patient_id', 'age', 'created_at', 'updated_at')
    inlines = [AppointmentInline, MedicalRecordInline]

    fieldsets = (
        ('Identity', {
            'fields': ('patient_id', ('first_name', 'last_name'), 'date_of_birth', ('gender', 'blood_group')),
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address'),
        }),
        ('Emergency Contact', {
            'fields': (('emergency_contact_name', 'emergency_contact_phone'),),
        }),
        ('Medical Background', {
            'fields': ('allergies', 'chronic_conditions'),
            'classes': ('collapse',),
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def age(self, obj):
        return f"{obj.age} years"
    age.short_description = "Age"


# ─── Appointment Admin ─────────────────────────────────────────────────────────
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_patient_id', 'doctor', 'appointment_date', 'appointment_time', 'appointment_type', 'status', 'notification_sent')
    list_display_links = ('get_patient_name',)
    list_filter = ('status', 'appointment_type', 'notification_sent', 'doctor')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__patient_id', 'doctor__last_name', 'reason')
    ordering = ('-appointment_date', '-appointment_time')
    date_hierarchy = 'appointment_date'
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'notification_sent')

    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', ('appointment_date', 'appointment_time'), 'appointment_type'),
        }),
        ('Status', {
            'fields': ('status', 'notification_sent'),
        }),
        ('Notes', {
            'fields': ('reason', 'notes'),
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_patient_name(self, obj):
        return obj.patient.full_name
    get_patient_name.short_description = "Patient"
    get_patient_name.admin_order_field = 'patient__last_name'

    def get_patient_id(self, obj):
        return obj.patient.patient_id
    get_patient_id.short_description = "Patient ID"


# ─── Medical Record Admin ──────────────────────────────────────────────────────
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_patient_id', 'doctor', 'visit_date', 'chief_complaint_short', 'has_vitals', 'follow_up_date')
    list_display_links = ('get_patient_name',)
    list_filter = ('doctor', 'follow_up_date')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__patient_id', 'chief_complaint', 'diagnosis')
    ordering = ('-visit_date',)
    date_hierarchy = 'visit_date'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [VitalSignInline]

    fieldsets = (
        ('Patient & Doctor', {
            'fields': ('patient', 'doctor', 'appointment', 'visit_date'),
        }),
        ('Clinical Documentation', {
            'fields': ('chief_complaint', 'diagnosis', 'treatment'),
        }),
        ('Prescription & Notes', {
            'fields': ('prescription', 'notes', 'follow_up_date'),
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_patient_name(self, obj):
        return obj.patient.full_name
    get_patient_name.short_description = "Patient"
    get_patient_name.admin_order_field = 'patient__last_name'

    def get_patient_id(self, obj):
        return obj.patient.patient_id
    get_patient_id.short_description = "Patient ID"

    def chief_complaint_short(self, obj):
        return obj.chief_complaint[:60] + '...' if len(obj.chief_complaint) > 60 else obj.chief_complaint
    chief_complaint_short.short_description = "Chief Complaint"

    def has_vitals(self, obj):
        return obj.vitals.exists()
    has_vitals.short_description = "Vitals Recorded"
    has_vitals.boolean = True


# ─── Vital Sign Admin ──────────────────────────────────────────────────────────
@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ('get_patient', 'get_visit_date', 'temperature', 'blood_pressure', 'pulse_rate', 'oxygen_saturation', 'bmi_display')
    list_filter = ('record__visit_date',)
    search_fields = ('record__patient__first_name', 'record__patient__last_name', 'record__patient__patient_id')
    readonly_fields = ('recorded_at', 'bmi_display')

    fieldsets = (
        ('Record Reference', {
            'fields': ('record',),
        }),
        ('Cardiovascular', {
            'fields': (('blood_pressure_systolic', 'blood_pressure_diastolic'), 'pulse_rate'),
        }),
        ('Respiratory & Oxygenation', {
            'fields': ('respiratory_rate', 'oxygen_saturation', 'temperature'),
        }),
        ('Body Metrics', {
            'fields': (('weight', 'height'), 'bmi_display'),
        }),
        ('Recorded', {
            'fields': ('recorded_at',),
            'classes': ('collapse',),
        }),
    )

    def get_patient(self, obj):
        return obj.record.patient.full_name
    get_patient.short_description = 'Patient'
    get_patient.admin_order_field = 'record__patient__last_name'

    def get_visit_date(self, obj):
        return obj.record.visit_date
    get_visit_date.short_description = 'Visit Date'
    get_visit_date.admin_order_field = 'record__visit_date'

    def blood_pressure(self, obj):
        if obj.blood_pressure_systolic and obj.blood_pressure_diastolic:
            return f"{obj.blood_pressure_systolic}/{obj.blood_pressure_diastolic} mmHg"
        return "—"
    blood_pressure.short_description = "Blood Pressure"

    def bmi_display(self, obj):
        if obj.bmi:
            return f"{obj.bmi} kg/m²"
        return "—"
    bmi_display.short_description = "BMI"


# ─── Admin Site Customisation ──────────────────────────────────────────────────
admin.site.site_header = "MediCare HMS Administration"
admin.site.site_title = "MediCare HMS"
admin.site.index_title = "Hospital Management Portal"
