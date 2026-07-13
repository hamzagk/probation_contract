# Setting Up Outlook Email for HR Portal

## Switching from Gmail to Outlook

To configure the HR portal to use Outlook instead of Gmail, follow these steps:

### 1. Outlook Account Setup

For Outlook/Hotmail accounts, you need to enable "Less secure app access" or use an "App Password":

#### Option A: Using App Password (Recommended)
1. Sign in to your Microsoft account at https://account.microsoft.com/
2. Go to "Security" section
3. Under "App passwords & two-factor authentication", select "Two-step verification"
4. Turn it ON if not already enabled
5. Generate a new "App password" for "Mail"
6. Use this 16-character app password in place of your regular password

#### Option B: If not using 2FA
1. You may need to allow "Less secure app access" in your Microsoft account settings
2. Note: This option is less secure and Microsoft may disable it

### 2. Update the .env File

Update your .env file with the following Outlook SMTP settings:

```
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=muhammad.hamza@giki.edu.pk
EMAIL_HOST_PASSWORD=your-outlook-app-password
DEFAULT_FROM_EMAIL=muhammad.hamza@giki.edu.pk
HR_EMAIL=muhammad.hamza@giki.edu.pk
```

Replace:
- `muhammad.hamza@giki.edu.pk` with your actual email address
- `your-outlook-app-password` with the 16-character app password you generated

### 3. Enhanced Email Templates with CC Functionality

The system now includes:
- Advanced HTML email templates with GIK Institute branding
- CC functionality that sends copies to HR (muhammad.hamza@giki.edu.pk) for all notifications
- Progress bars showing probation completion status
- Responsive design for mobile devices
- Professional styling with GIK colors (blue and gold)

### 4. CC Functionality Explained

The system automatically sends CC copies of all probation notifications to:
- Primary recipient: Department head (based on employee's department)
- CC recipient: HR department (muhammad.hamza@giki.edu.pk)

This ensures HR is always informed about probation-related communications.

### 5. Email Types with CC

The following email notifications now include CC functionality:
- Automatic probation expiration alerts
- Manual email notifications sent from the employee list page
- Department-specific notifications

### 6. Testing Email Configuration

After updating the .env file:
1. Restart the server
2. Trigger a probation notification (either manually or wait for automatic notifications)
3. Check both the primary recipient and CC recipient for received emails

### 7. Troubleshooting Common Issues

**Issue**: "Authentication failed" error
**Solution**: Verify your app password is correct and that 2FA is enabled

**Issue**: "Connection refused" error
**Solution**: Verify the SMTP settings (host, port, TLS)

**Issue**: Emails not being sent
**Solution**: Check firewall settings and ensure port 587 is not blocked

### 8. Outlook SMTP Settings Reference

- **SMTP Server**: smtp-mail.outlook.com
- **Port**: 587 (for TLS) or 995 (for SSL)
- **Encryption**: TLS
- **Authentication**: Required
- **Username**: Your full Outlook email address
- **Password**: App password (recommended) or account password

### 9. Maintaining GIK Brand Identity

The enhanced email templates feature:
- GIK Institute blue and gold color scheme
- Professional typography and layout
- Responsive design for all devices
- Watermark and branding elements
- Consistent with GIK's institutional identity

### 10. Security Best Practices

- Always use app passwords instead of account passwords when possible
- Regularly rotate app passwords
- Monitor email logs for unauthorized access
- Keep the .env file secure and never commit to version control