# Setting Up Automatic Email Functionality

## Prerequisites

The automatic email notifications rely on Celery and Redis for scheduling. Here's how to set them up:

### 1. Install Redis (Windows)

1. Download Redis for Windows from: https://github.com/tporadowski/redis/releases
2. Extract and run `redis-server.exe`
3. Verify Redis is running by executing `redis-cli ping` - should return "PONG"

### 2. Start Celery Worker and Beat

Open two separate command prompts in your project directory:

Terminal 1 (Celery Worker):
```bash
celery -A hr_project worker --loglevel=info
```

Terminal 2 (Celery Beat - Scheduler):
```bash
celery -A hr_project beat --loglevel=info
```

### 3. Alternative: Manual Trigger

If you can't install Redis, you can manually trigger the email notifications:

```bash
# Send daily probation notifications
python manage.py trigger_automatic_emails --type daily

# Send weekly probation report
python manage.py trigger_automatic_emails --type weekly
```

### 4. Windows Task Scheduler Setup (Recommended Alternative)

For Windows systems without Redis, use the Windows Task Scheduler with the provided batch file:

1. Open Windows Task Scheduler
2. Create a Basic Task
3. Set it to run weekly on Tuesday at 9:00 AM
4. Choose "Start a program" as the action
5. Browse to the `run_automatic_emails.bat` file in your project directory
6. Set the "Start in" directory to your project directory

Or run the batch file manually to test:
```batch
run_automatic_emails.bat
```

### 5. Alternative Management Command

You can also use the new management command that's Windows-friendly:
```bash
python manage.py run_automatic_emails
```

This command checks if today is Tuesday and sends the appropriate emails accordingly.

## Email Configuration

Make sure your `.env` file has the correct email settings:

```
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
HR_EMAIL=hr@company.com
```

Note: For Gmail, you need to use an App Password, not your regular password.

## Testing Email Functionality

You can test the email functionality with:

```bash
# Test the management command
python manage.py send_probation_notifications

# Test the automatic emails
python manage.py run_automatic_emails

# Test the custom email functionality from the employee list page
# (This works without Celery)
```

## Troubleshooting

1. If emails are not sending, check your email settings in `.env`
2. For Gmail, ensure you're using an App Password
3. Check that your firewall is not blocking SMTP connections
4. Verify that the email addresses in settings.py are correct
5. If using the batch file, ensure the path is correct and the virtual environment is activated