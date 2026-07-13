# Deployment Guide for HR Portal

This guide explains how to deploy the HR Portal application to various platforms.

## PythonAnywhere Deployment

### Step 1: Sign Up and Create a New Web App
1. Go to [PythonAnywhere](https://www.pythonanywhere.com/)
2. Create a free account
3. Click on "Web" tab and then "Add a new web app"
4. Choose "Manual Configuration" and Python 3.12
5. Follow the wizard to create the app

### Step 2: Upload Your Code
1. Go to the "Files" tab
2. Upload your project files or clone from a repository
3. Or use the console to git clone your repository

### Step 3: Configure Virtual Environment
1. Go to the "Consoles" tab and start a "Bash" console
2. Create a virtual environment:
```bash
mkvirtualenv --python=/usr/bin/python3.12 hrportal_env
```

3. Activate the virtual environment:
```bash
workon hrportal_env
```

4. Install dependencies:
```bash
cd ~/my-site-name  # Replace with your project directory
pip install -r requirements.txt
```

### Step 4: Configure the Application
1. In the "Web" tab, configure these settings:

**Code section:**
- Source code: `/home/yourusername/my-site-name` (replace with your project path)
- Working directory: `/home/yourusername/my-site-name`

**Virtualenv section:**
- Path: `/home/yourusername/.virtualenvs/hrportal_env`

### Step 5: Set Environment Variables
1. In the "Web" tab, scroll down to "Environment variables"
2. Add these variables:
```
SECRET_KEY=your_very_long_secret_key_here
DEBUG=False
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
OPENAI_API_KEY=your_openai_api_key
```

### Step 6: Configure Static Files
1. In the "Web" tab, in the "Static files" section:
- URL: `/static/`
- Directory: `/home/yourusername/my-site-name/staticfiles`

### Step 7: Run Migrations and Collect Static Files
1. Go to the "Consoles" tab and start a "Bash" console
2. Run these commands:
```bash
workon hrportal_env
cd ~/my-site-name  # Replace with your project directory
python manage.py collectstatic
python manage.py migrate
python manage.py createsuperuser  # Create your admin user
```

### Step 8: Reload the Web App
1. Go back to the "Web" tab
2. Click the "Reload" button

## Heroku Deployment

### Prerequisites
1. Install Heroku CLI
2. Have a Heroku account

### Steps
1. Create a new Heroku app:
```bash
heroku create your-app-name
```

2. Set environment variables:
```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set EMAIL_HOST_USER="muhammad.hamza@giki.edu.pk"
heroku config:set EMAIL_HOST_PASSWORD="your-app-password"
heroku config:set OPENAI_API_KEY="your-openai-api-key"
```

3. Deploy the app:
```bash
git push heroku main
```

4. Run migrations:
```bash
heroku run python manage.py migrate
heroku run python manage.py collectstatic
heroku run python manage.py createsuperuser
```

## Render Deployment

### Steps
1. Create a new Web Service on Render
2. Connect to your GitHub repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `gunicorn hr_project.wsgi`
5. Set environment variables in the Render dashboard
6. Deploy!

## Environment Variables Required

- `SECRET_KEY`: Django secret key (required, should be long and random)
- `DEBUG`: Set to False in production (optional, default: False)
- `EMAIL_HOST_USER`: Email address for sending notifications
- `EMAIL_HOST_PASSWORD`: App password for email account
- `OPENAI_API_KEY`: Your OpenAI API key (optional if not using AI features)
- `DATABASE_URL`: Database connection string (for production deployments)

## Default Login Credentials

After first deployment, you should create a superuser:
```bash
python manage.py createsuperuser
```

Or use these defaults if created automatically:
- Username: `admin`
- Password: `admin123`