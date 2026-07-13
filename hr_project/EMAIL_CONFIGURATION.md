# Email Configuration Guide for HR Portal

## Setting up Gmail for Email Notifications

To use Gmail for sending email notifications from your HR Portal, you need to configure App Passwords.

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security
3. Under "Signing in to Google," select 2-Step Verification
4. Follow the steps to enable 2FA

### Step 2: Generate an App Password
1. In your Google Account, go to Security
2. Under "Signing in to Google," select App passwords
3. Select "Mail" as the app and "Windows Computer" (or your device) as the device
4. Click "Generate"
5. Copy the 16-character password

### Step 3: Update Environment Variables
Replace the values in your `.env` file:

```
EMAIL_HOST_USER=muhammad.hamza@giki.edu.pk
EMAIL_HOST_PASSWORD=your-16-character-app-password
DEFAULT_FROM_EMAIL=muhammad.hamza@giki.edu.pk
HR_EMAIL=muhammad.hamza@giki.edu.pk
```

### Step 4: Alternative Email Providers
If you prefer not to use Gmail, you can configure other email providers:

#### Outlook/Hotmail:
```
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=muhammad.hamza@giki.edu.pk
EMAIL_HOST_PASSWORD=your-password
```

#### Yahoo Mail:
```
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=muhammad.hamza@giki.edu.pk
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Testing Email Configuration
To test if your email configuration is working:

1. Start the development server: `python manage.py runserver`
2. Go to the Django shell: `python manage.py shell`
3. Run the following code:
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

### Important Notes:
- Never commit your `.env` file to version control
- Use strong, unique passwords
- Regularly review and rotate your app passwords
- For production, consider using dedicated email services like SendGrid, Mailgun, or Amazon SES