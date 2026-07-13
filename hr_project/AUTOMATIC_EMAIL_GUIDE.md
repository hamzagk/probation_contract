# Automatic Email Setup Guide

## Overview
The HR Portal automatically sends probation reports via email. Here's how it works:

## Email Schedule

### Weekly Probation Report
- **When**: Every Tuesday at 9:00 AM
- **Recipients**: 
  - muhammad.hamza@giki.edu.pk
  - muhammad.hamza@giki.edu.pk
- **Content**: List of all employees with probation ending in the next 30 days
- **Excludes**: Associate Professors (they don't have probation)

### Daily Notifications
- **When**: Can be run manually any day
- **Recipients**: Department heads and HR
- **Content**: Employees with less than 15 days remaining in probation

## Why Emails Are Not Being Sent

### Common Issues:

1. **Today is not Tuesday**
   - The weekly report only runs on Tuesdays
   - Check current day: `python -c "from datetime import datetime; print(datetime.now().strftime('%A'))"`

2. **Celery/Redis Not Running**
   - The automatic scheduler requires Celery and Redis
   - See "Running Celery" section below

3. **Email Configuration Issues**
   - Check `.env` file for correct email settings
   - Ensure EMAIL_HOST_PASSWORD is correct (Gmail App Password)

## How to Run Manually

### Option 1: Run Weekly Report Any Day
```bash
python manage.py send_weekly_probation_report
```

### Option 2: Run Automatic Emails (Daily + Weekly if Tuesday)
```bash
python manage.py run_automatic_emails
```

### Option 3: Use Batch File (Windows)
```batch
run_automatic_emails.bat
```

### Option 4: Test Report (Preview)
```bash
python test_weekly_report.py
```

## Running Celery (For Automatic Scheduling)

### Prerequisites
1. Install Redis: https://github.com/tporadowski/redis/releases
2. Start Redis Server: Run `redis-server.exe`

### Start Celery Worker
```bash
celery -A hr_project worker --loglevel=info
```

### Start Celery Beat (Scheduler)
```bash
celery -A hr_project beat --loglevel=info
```

## Windows Task Scheduler Setup (Recommended)

For automatic emails without running Celery:

1. Open **Windows Task Scheduler**
2. Create a **Basic Task**
3. Name: "HR Portal Weekly Probation Report"
4. Trigger: **Weekly** on **Tuesday** at **9:00 AM**
5. Action: **Start a program**
6. Program: `C:\Users\Hamza\.qwen\projects\hr_project\run_automatic_emails.bat`
7. Start in: `C:\Users\Hamza\.qwen\projects\hr_project`

## Email Configuration

Edit `.env` file:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
HR_EMAIL=muhammad.hamza@giki.edu.pk
```

### Getting Gmail App Password
1. Go to Google Account Settings
2. Security → 2-Step Verification
3. App Passwords
4. Select "Mail" and your device
5. Copy the generated password

## Probation Rules

### Who Has Probation?
- Assistant Professors
- Lecturers
- Engineers
- Administrative staff
- All other employees

### Who Does NOT Have Probation?
- **Associate Professors** (automatically marked as "Completed")

## Testing

### Test Email Connection
```bash
python test_email.py
```

### Test Weekly Report
```bash
python test_weekly_report.py
```

### Check Email Settings
```bash
python check_email_settings.py
```

## Troubleshooting

### Emails Not Sending
1. Check `.env` file for correct credentials
2. Test email: `python test_email.py`
3. Check spam folder
4. Verify Gmail App Password (not regular password)

### Wrong Employees in Report
1. Associate Professors should be excluded automatically
2. Run: `python update_associate_professors.py` to fix status

### Celery Not Working
1. Ensure Redis is running: `redis-cli ping` should return "PONG"
2. Check Celery worker logs for errors
3. Restart Celery worker and beat

## Files Reference

- `run_automatic_emails.bat` - Windows batch file to run emails
- `test_weekly_report.py` - Preview weekly report
- `update_associate_professors.py` - Fix Associate Professor status
- `hr_portal/management/commands/run_automatic_emails.py` - Management command
- `hr_portal/management/commands/send_weekly_probation_report.py` - Weekly report command
- `hr_portal/tasks.py` - Celery tasks
