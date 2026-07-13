# PythonAnywhere Deployment Guide for GIK Institute HR Portal

## Overview
This guide will help you deploy the GIK Institute HR Portal to PythonAnywhere, allowing it to run continuously even when you close VS Code.

## Prerequisites
- A PythonAnywhere account (free tier is sufficient)
- Your GitHub repository URL (if deploying from GitHub)

## Step-by-Step Deployment Process

### 1. Log into PythonAnywhere
- Go to https://www.pythonanywhere.com/
- Sign in to your account

### 2. Create a New Web App
- Click on the "Web" tab
- Click "Add a new web app"
- Choose "Manual configuration" (at the bottom)
- Select your Python version (Python 3.12 recommended)
- Click "Next" to proceed

### 3. Configure Your Virtual Environment
- You'll be taken to the web app configuration page
- Under "Virtualenv", click "Enter path to virtualenv" 
- Click "Create a new virtualenv"
- Wait for the virtual environment to be created

### 4. Access Your PythonAnywhere Console
- Click on the "Consoles" tab
- Launch a "Bash" console
- Navigate to your project directory:
```bash
cd ~/my-site-name  # Replace 'my-site-name' with your actual site name
```

### 5. Clone Your Repository (Alternative Method)
If you prefer to clone directly to PythonAnywhere:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
mv YOUR_REPOSITORY/* .
rmdir YOUR_REPOSITORY
```

### 6. Install Dependencies
```bash
pip3 install --user -r requirements_pythonanywhere.txt
```

### 7. Set Up Environment Variables
Run these commands to set up your environment variables:
```bash
echo "export SECRET_KEY='$(openssl rand -hex 40)'" >> ~/.bashrc
echo "export DEBUG=False" >> ~/.bashrc
echo "export ALLOWED_HOSTS='.pythonanywhere.com,your_domain.pythonanywhere.com'" >> ~/.bashrc
echo "export EMAIL_HOST_USER='your_email@gmail.com'" >> ~/.bashrc
echo "export EMAIL_HOST_PASSWORD='your_app_password'" >> ~/.bashrc
source ~/.bashrc
```

### 8. Configure Your Django Project
- Go back to the "Web" tab
- Click "Reload" for your site to pick up the bashrc environment variables
- Edit your WSGI file by clicking the link near the top of the page ("Edit this file" next to "WSGI configuration file:")
- Replace the contents with:

```python
import os
import sys

# Add your project directory to the Python path
path = '/home/YOUR_USERNAME/YOUR_SITE_NAME'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'hr_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 9. Update Your Django Settings
Edit your Django settings.py file to work with PythonAnywhere:
- Change the database settings to use SQLite or PostgreSQL
- Update STATIC_ROOT and STATICFILES_DIRS
- Make sure ALLOWED_HOSTS includes your PythonAnywhere domain

### 10. Run Django Migrations
In the PythonAnywhere Bash console:
```bash
cd ~/my-site-name  # Replace with your actual directory
python3 manage.py migrate
```

### 11. Create a Superuser (Optional)
```bash
python3 manage.py createsuperuser
```

### 12. Collect Static Files
```bash
python3 manage.py collectstatic
```

### 13. Reload Your Web App
- Go back to the "Web" tab
- Click the "Reload" button for your web app

## Environment Variables Setup

Add these environment variables to your `.bashrc` file on PythonAnywhere:

```bash
# Django settings
export SECRET_KEY='your-secret-key-here'
export DEBUG=False
export ALLOWED_HOSTS='.pythonanywhere.com,your_username.pythonanywhere.com'

# Email settings (for Gmail)
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER=your_email@gmail.com
export EMAIL_HOST_PASSWORD=your_app_password

# HR email settings
export HR_EMAIL=hr_email@example.com
export CS_DEPT_EMAIL=cs_dept@example.com
export EE_DEPT_EMAIL=ee_dept@example.com
# Add other department emails as needed
```

## Troubleshooting

1. **Import Errors**: Make sure all dependencies are installed in the virtual environment
2. **Database Issues**: Ensure your database is properly migrated
3. **Static Files**: Run `collectstatic` after any changes to static files
4. **Permission Issues**: Make sure your files have the correct permissions

## Updating Your Application

When you need to update your application:
1. Pull the latest changes: `git pull origin main`
2. Install any new dependencies: `pip3 install --user -r requirements_pythonanywhere.txt`
3. Run migrations: `python3 manage.py migrate`
4. Collect static files: `python3 manage.py collectstatic`
5. Reload the web app from the "Web" tab

## Keeping Your Server Online

Once deployed to PythonAnywhere, your application will remain online 24/7 as long as:
- Your PythonAnywhere account remains active
- You're using the paid tier OR refresh your free account daily
- No major configuration errors occur

## Important Notes

- Free accounts on PythonAnywhere sleep after 30 minutes of inactivity but wake up when accessed
- Paid accounts remain active at all times
- For production use, consider upgrading to a paid plan
- Remember to use Gmail App Passwords if using Gmail for email notifications