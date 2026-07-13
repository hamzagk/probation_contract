# Setting Up Email Notifications for HR Portal

## Resolving Gmail Authentication Issues

To fix the "Username and Password not accepted" error, you need to set up an App Password for your Gmail account since you have 2FA enabled.

### Steps to Create a Gmail App Password:

1. **Enable 2-Step Verification** (if not already enabled):
   - Go to your Google Account
   - Click on Security
   - Under "Signing in to Google," select 2-Step Verification
   - Follow the steps to turn it on

2. **Generate an App Password**:
   - Go to your Google Account
   - Click on Security
   - Under "Signing in to Google," select App passwords
   - Select the app (Mail) and device (Other - custom name like "HRPortal")
   - Click Generate
   - Copy the 16-character password

3. **Update the .env file**:
   - Open `.env` file in the project root
   - Find the line: `EMAIL_HOST_PASSWORD=your-app-password-here`
   - Replace `your-app-password-here` with the 16-character app password you copied
   - Save the file

4. **Restart the server**:
   - Stop the server: `taskkill /F /T /PID <current_pid>`
   - Restart: Run `start_server.bat`

### Email Configuration in the System:

- **Primary Sending Email**: muhammad.hamza@giki.edu.pk (configured as EMAIL_HOST_USER)
- **Primary Receiving Email**: muhammad.hamza@giki.edu.pk (configured as HR_EMAIL)
- **Department Emails**: Various departmental emails as defined in .env

### Testing Email Functionality:

After setting up the app password and restarting the server:
1. Access the HR portal at http://127.0.0.1:8000/
2. Perform an action that triggers email notifications (like adding/modifying employee records)
3. Check both muhammad.hamza@giki.edu.pk and muhammad.hamza@giki.edu.pk for received emails

### Troubleshooting:

If you still encounter issues:
1. Double-check that you're using the App Password, not your regular Gmail password
2. Ensure the App Password has been correctly entered in the .env file
3. Verify that 2-Step Verification is enabled on your account
4. Make sure you selected "Mail" when generating the App Password