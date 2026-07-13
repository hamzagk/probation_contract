# Email Management System for HR Portal

## Overview
The HR Portal now includes a comprehensive email management system that allows administrators to dynamically manage department email addresses through the Django admin interface.

## How to Add/Edit Email Addresses

### Method 1: Using Django Admin Interface (Recommended)

1. **Access the Admin Panel**
   - Navigate to `http://127.0.0.1:8000/admin/`
   - Log in with your admin credentials

2. **Navigate to Departments**
   - In the admin panel, find and click on "Departments" under the "Hr portal" section
   - If you don't see it, you may need to run migrations first

3. **Add a New Department**
   - Click "ADD DEPARTMENT" button
   - Fill in the required fields:
     - **Name**: The name of the department (e.g., "Computer Science")
     - **Email**: The email address for the department head
     - **Description**: Optional description of the department
   - Click "SAVE"

4. **Edit Existing Department**
   - Click on the department name in the list
   - Update the email address or other information
   - Click "SAVE"

### Method 2: Using Management Command

1. **Run the Setup Command**
   ```bash
   python manage.py setup_departments
   ```
   This command will create default departments with placeholder email addresses.

2. **Manually Add Departments via Shell**
   ```bash
   python manage.py shell
   ```
   Then run:
   ```python
   from hr_portal.models import Department
   
   # Create a new department
   dept = Department.objects.create(
       name="New Department Name",
       email="muhammad.hamza@giki.edu.pk",
       description="Description of the department"
   )
   ```

## Email Configuration for Sending Notifications

### Environment Variables Setup

Update your `.env` file with the following email configuration:

```
# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=muhammad.hamza@giki.edu.pk
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=muhammad.hamza@giki.edu.pk
HR_EMAIL=muhammad.hamza@giki.edu.pk
```

### For Gmail Users:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Navigate to Security → App passwords
   - Generate a password for "Mail" and your device
   - Use this 16-character password in EMAIL_HOST_PASSWORD

### For Other Email Providers:
- **Outlook/Hotmail**: Use `smtp-mail.outlook.com` as EMAIL_HOST
- **Yahoo**: Use `smtp.mail.yahoo.com` as EMAIL_HOST
- **Custom SMTP**: Use your provider's SMTP server details

## How the Email System Works

1. **Department-Based Emails**: When sending notifications, the system first checks the Department model for the specific department's email address.

2. **Fallback System**: If a department doesn't have an email configured, the system falls back to the HR_EMAIL defined in settings.

3. **Dynamic Updates**: Changes to department emails in the admin panel take effect immediately without restarting the server.

## Running Migrations

After making model changes, run these commands:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Testing Email Configuration

To test if your email configuration is working:

1. **Using Django Shell**:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.core.mail import send_mail
   
   send_mail(
       'Test Subject',
       'Test message.',
       'from@example.com',
       ['to@example.com'],
       fail_silently=False,
   )
   ```

2. **Using Admin Interface**:
   - Add a test department with your email
   - Trigger a probation notification from the dashboard
   - Check if the email is sent successfully

## Troubleshooting Common Issues

### Issue: Email authentication error
**Solution**: Verify your email credentials and ensure you're using an App Password for Gmail, not your regular password.

### Issue: Department emails not showing up
**Solution**: Make sure you've run migrations after updating the models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: Emails not sending
**Solution**: Check your email settings in the `.env` file and ensure your email provider allows sending emails via SMTP.

## Security Best Practices

- Never commit your `.env` file to version control
- Use strong, unique passwords/App passwords
- Regularly review and rotate your email credentials
- Limit admin access to trusted personnel only
- Monitor email logs for any unauthorized usage

## Updating Employee Records

When adding or updating employees, you can now assign them to departments that have email addresses configured:

1. Go to the Employees section in the admin panel
2. When creating or editing an employee, select the appropriate department from the dropdown
3. The system will automatically use that department's email for notifications