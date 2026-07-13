# GIK Institute HR Portal - Complete Documentation

## Project Overview

The GIK Institute HR Portal is a comprehensive HR management system built with Django. It provides features for employee management, probation tracking, document generation, and automated notifications.

## Features

- **Employee Management**: Track employee information with S.#, Name, Designation, Department, and Start/End Dates
- **Automated Probation Tracking**: Automatic calculation of 6-month probation periods with 15-day advance notifications
- **Document Management**: Upload and manage Excel/Word documents for employees
- **Excel Import/Export**: Bulk import employee data from Excel files and export reports
- **AI Document Assistant**: Generate professional documents like certificates, letters, and notes using AI
- **Attractive Dashboard**: Visualize employee data and probation status with charts
- **Email Notifications**: Automated emails for upcoming probation expirations
- **Authentication System**: Secure login/logout functionality

## Technical Stack

- **Backend**: Python 3.12, Django 4.2.7
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Database**: SQLite (default), PostgreSQL (recommended for production)
- **Server**: Gunicorn (production), Django development server (development)
- **Deployment**: Multiple platforms supported (Heroku, Render, Railway, PythonAnywhere, GCP)

## GIK Institute Departments

The system includes specific departments for GIK Institute:

- FCSE (Faculty of Computer Systems Engineering)
- FEE (Faculty of Electrical Engineering)
- FBS/FES (Faculty of Basic Sciences / Faculty of Earth Sciences)
- DChE (Department of Chemical Engineering)
- DCvE (Department of Civil Engineering)
- FMCE (Faculty of Mechanical and Chemical Engineering)
- FME (Faculty of Materials and Metallurgical Engineering)
- SMgS (School of Mining and Geological Sciences)
- HR (Human Resources Department)
- Admin (Administration Department)
- Facilitation (Facilitation Services)
- Procurement (Procurement Department)
- Hostels (Hostel Management)
- A&E (Architecture and Engineering)
- Finance (Finance Department)
- Rector (Office of the Rector)
- Pro-Rector (Admin) (Pro-Rector Administration)
- Pro-Rector (Academic) (Pro-Rector Academic Affairs)

## Deployment Options

### 1. Render
- Generous free tier
- Easy GitHub integration
- Automatic SSL
- Recommended for production

### 2. Railway
- Excellent free tier
- Developer-friendly
- Quick setup
- Good for development/testing

### 3. PythonAnywhere
- Python-specific platform
- Easy setup
- Good for learning
- Limited scalability

### 4. Heroku
- Beginner-friendly
- Good documentation
- Sleeps after inactivity on free tier
- Good for prototyping

### 5. Google Cloud Platform (Cloud Run)
- Highly scalable
- Professional infrastructure
- More complex setup
- Best for enterprise

## Environment Variables Required

- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST_USER`: Email address for sending notifications
- `EMAIL_HOST_PASSWORD`: App password for email account
- `DATABASE_URL`: PostgreSQL database URL (for production)

## Default Credentials

After first deployment, a default superuser will be created:
- Username: `admin`
- Password: `admin123`

## Local Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Start the server: `python manage.py runserver`

## Production Deployment

1. Choose a deployment platform (Render, Railway, GCP, etc.)
2. Set up environment variables
3. Configure the database
4. Run migrations
5. Collect static files
6. Deploy the application

## File Structure

```
hr_project/
├── hr_project/           # Django project settings
├── hr_portal/            # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── urls.py           # URL configurations
│   └── ...
├── templates/            # HTML templates
├── static/               # Static files
├── media/                # Media uploads
├── manage.py             # Django management script
├── requirements.txt      # Dependencies
├── runtime.txt           # Python version
├── Procfile              # Heroku deployment
├── README.md             # Project documentation
├── render.yaml           # Render deployment config
├── Dockerfile            # Container configuration
└── ...
```

## Security Considerations

- Never commit secret keys to version control
- Use environment variables for sensitive data
- Validate all user inputs
- Sanitize data before displaying
- Keep dependencies updated
- Use HTTPS in production

## Performance Optimization

- Use database indexing appropriately
- Optimize database queries
- Implement caching where appropriate
- Optimize static files
- Use CDN for static assets
- Monitor resource usage

## Support and Maintenance

- Regular security updates
- Database backups
- Performance monitoring
- Log analysis
- User support

## Contact Information

For support with the HR Portal application, contact the development team or refer to the Django documentation for any framework-related issues.