# Hospital Appointment & Records Management System

A Django-based system for managing hospital appointments, patient records, and staff. Built with function-based views.

## Tech Stack
- **Backend:** Python / Django 5.0 (function-based views)
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Frontend:** HTML + Tailwind CSS (CDN)
- **SMS:** Arkesel SMS Gateway
- **Email:** SMTP (Gmail compatible)

## Project Structure

```
hospital_system/
├── hospital_system/       # Django project config
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── accounts/          # CustomUser, login, staff management
│   └── core/              # Patients, Appointments, Records, Analytics, Notifications
├── templates/
│   ├── base/              # base.html
│   ├── accounts/          # login, staff
│   ├── patients/          # list, detail, form
│   ├── appointments/      # list, today, detail, form
│   ├── records/           # list, detail, form, history
│   ├── dashboard/         # main dashboard
│   └── reports/           # analytics, daily report
├── static/                # CSS, JS, images
├── manage.py
└── requirements.txt
```

## Setup Instructions

### 1. Clone and set up virtual environment
```bash
git clone <repo>
cd hospital_system
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create admin/superuser
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## User Roles

| Role          | Access                                           |
|---------------|--------------------------------------------------|
| Admin         | Full access including staff management          |
| Doctor        | View patients, update records & appointments    |
| Nurse         | View patients and appointments                  |
| Receptionist  | Register patients, book appointments            |

## Key Features
- Secure login with role-based access
- Patient registration with auto-generated IDs (PAT-YYYY-NNNN)
- Appointment scheduling with status tracking
- Medical records with vital signs
- SMS & email notifications via Twilio and SMTP
- Analytics dashboard and daily reports
- Patient medical history retrieval

## SMS Reminders (Optional Cron Setup)
To send daily reminders, add to crontab:
```bash
# Runs every day at 8 AM
0 8 * * * /path/to/venv/bin/python /path/to/manage.py send_reminders
```
(Create a custom management command in apps/notifications/management/commands/send_reminders.py)
