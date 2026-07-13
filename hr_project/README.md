# GIK Institute HR Portal

An attractive and responsive HR management system with AI assistant for document generation, Excel import/export, and automated probation notifications.

## Features

- **Employee Management**: Track employee information with S.#, Name, Designation, Department, and Start/End Dates
- **Automated Probation Tracking**: Automatic calculation of 6-month probation periods with 15-day advance notifications
- **Document Management**: Upload and manage Excel/Word documents for employees
- **Excel Import/Export**: Bulk import employee data from Excel files and export reports
- **AI Document Assistant**: Generate professional documents like certificates, letters, and notes using AI
- **Attractive Dashboard**: Visualize employee data and probation status with charts
- **Email Notifications**: Automated emails for upcoming probation expirations
- **Authentication System**: Secure login/logout functionality

## Deployment Instructions

### Deploy to Heroku

1. Create a Heroku account at [https://heroku.com](https://heroku.com)
2. Install the Heroku CLI
3. Clone this repository
4. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
5. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
   heroku config:set EMAIL_HOST_PASSWORD="your-app-password"
   ```
6. Deploy the app:
   ```bash
   git push heroku main
   ```
7. Run migrations:
   ```bash
   heroku run python manage.py migrate
   ```

### Deploy to PythonAnywhere

#### Option 1: Manual Setup
1. Create an account at [https://pythonanywhere.com](https://pythonanywhere.com)
2. Create a new web app
3. Upload your code or clone from a repository
4. Install dependencies:
   ```bash
   pip3 install -r requirements_pythonanywhere.txt
   ```
5. Set environment variables in the PythonAnywhere dashboard or .bashrc file
6. Run migrations:
   ```bash
   python3 manage.py migrate
   ```
7. Collect static files:
   ```bash
   python3 manage.py collectstatic
   ```

#### Option 2: Using the Setup Script
1. Upload the `setup_pythonanywhere.py` and `requirements_pythonanywhere.txt` files to PythonAnywhere
2. Run the setup script:
   ```bash
   python3 setup_pythonanywhere.py
   ```

For detailed instructions, see the PYTHONANYWHERE_DEPLOYMENT_GUIDE.md file.

### Deploy to Render

1. Create an account at [https://render.com](https://render.com)
2. Create a new Web Service
3. Connect to your GitHub repository
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `gunicorn hr_project.wsgi`
6. Set environment variables in the Render dashboard
7. Deploy!

### Deploy to Railway

1. Create an account at [https://railway.app](https://railway.app)
2. Create a new project
3. Connect to your GitHub repository
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `python manage.py migrate && python manage.py collectstatic --noinput && gunicorn hr_project.wsgi:application --log-file -`
6. Set environment variables in the Railway dashboard, including `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `DATABASE_URL`
7. Deploy!

## Environment Variables

- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Set to False in production (optional, default: False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (optional, default: localhost,127.0.0.1)
- `CSRF_TRUSTED_ORIGINS`: Comma-separated HTTPS origins for production
- `EMAIL_HOST_USER`: Email address for sending notifications
- `EMAIL_HOST_PASSWORD`: App password for email account
- `DATABASE_URL`: PostgreSQL database URL for production deployments
- `REDIS_URL`: Redis URL for Celery and scheduled jobs

## Default Login Credentials

After first deployment, a default superuser will be created:
- Username: `admin`
- Password: `admin123`

## Local Development

To run locally:
1. Install dependencies: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Create a superuser: `python manage.py createsuperuser`
4. Start the server: `python manage.py runserver`

## Support

For support, contact the development team or refer to the Django documentation for any framework-related issues.