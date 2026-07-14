import os
from pathlib import Path
from decouple import config

# Import dj_database_url with fallback for environments where it's not installed
try:
    import dj_database_url
    DJ_DATABASE_URL_AVAILABLE = True
except ImportError:
    DJ_DATABASE_URL_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    host.strip()
    for host in config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
    if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in config('CSRF_TRUSTED_ORIGINS', default='').split(',')
    if origin.strip()
]

# For PythonAnywhere deployment
if 'pythonanywhere' in os.getenv('HOSTNAME', ''):
    ALLOWED_HOSTS = ['.pythonanywhere.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hr_portal',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Added for serving static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hr_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hr_project.wsgi.application'

# Database
if DJ_DATABASE_URL_AVAILABLE:
    # Parse DATABASE_URL environment variable for production databases
    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///db.sqlite3',  # Fallback to SQLite if DATABASE_URL is not set
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to SQLite if dj_database_url is not available
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (Uploaded documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HTTPS hardening (Koyeb terminates TLS in front, so these are safe on Koyeb
# and on any other platform that fronts Django with a TLS proxy).
# Default to False so local dev over plain HTTP still works; set
# SECURE_SSL_REDIRECT=True in the production environment.
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)

# Allow all host headers
# ALLOWED_HOSTS = ['*']  # Commenting out to use the earlier configuration

# Static asset configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/admin/logout/'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='muhammad.hamza@giki.edu.pk')  # Your email address
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')  # Your email password or app password
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='muhammad.hamza@giki.edu.pk')

# HR email for notifications
HR_EMAIL = config('HR_EMAIL', default='muhammad.hamza@giki.edu.pk')  # Replace with actual HR email

# Shared secret for external cron (cron-job.org / GitHub Actions) hitting /cron/trigger-emails/
CRON_TOKEN = config('CRON_TOKEN', default='')
MONTHLY_PROBATION_REPORT_TEST_RECIPIENT = config(
    'MONTHLY_PROBATION_REPORT_TEST_RECIPIENT',
    default=HR_EMAIL,
)

# Additional email addresses for notifications
HR_EMAIL_LIST = [
    'muhammad.hamza@giki.edu.pk',
    'muhammad.hamza@giki.edu.pk',
    'nasirali@giki.edu.pk'
]

# Department email addresses
CS_DEPT_EMAIL = config('CS_DEPT_EMAIL', default='nasirali@giki.edu.pk')
EE_DEPT_EMAIL = config('EE_DEPT_EMAIL', default='nasirali@giki.edu.pk')
ME_DEPT_EMAIL = config('ME_DEPT_EMAIL', default='nasirali@giki.edu.pk')
MATH_DEPT_EMAIL = config('MATH_DEPT_EMAIL', default='nasirali@giki.edu.pk')
PHYSICS_DEPT_EMAIL = config('PHYSICS_DEPT_EMAIL', default='nasirali@giki.edu.pk')
CHEMISTRY_DEPT_EMAIL = config('CHEMISTRY_DEPT_EMAIL', default='nasirali@giki.edu.pk')
BIOLOGY_DEPT_EMAIL = config('BIOLOGY_DEPT_EMAIL', default='nasirali@giki.edu.pk')
BUSINESS_DEPT_EMAIL = config('BUSINESS_DEPT_EMAIL', default='nasirali@giki.edu.pk')
HUMANITIES_DEPT_EMAIL = config('HUMANITIES_DEPT_EMAIL', default='nasirali@giki.edu.pk')
OTHER_DEPT_EMAIL = config('OTHER_DEPT_EMAIL', default='muhammad.hamza@giki.edu.pk')

# OpenAI API key
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')

# Celery settings
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Celery Beat Schedule for automatic probation notifications
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-probation-notifications': {
        'task': 'hr_portal.tasks.send_probation_notifications_task',
        'schedule': crontab(minute=0, hour=9, day_of_week=2),  # Run weekly on Tuesday at 9 AM
    },
    'send-contract-expiration-notifications': {
        'task': 'hr_portal.tasks.send_contract_expiration_notifications_task',
        'schedule': crontab(minute=0, hour=9),  # Run daily at 9 AM
    },
    'send-weekly-employees-report': {
        'task': 'hr_portal.tasks.send_weekly_employees_report',
        'schedule': crontab(minute=0, hour=9, day_of_week=2),  # Run weekly on Tuesday at 9 AM
    },
    'send-weekly-probation-report': {
        'task': 'hr_portal.tasks.send_weekly_probation_report_task',
        'schedule': crontab(minute=30, hour=9, day_of_week=2),  # Run weekly on Tuesday at 9:30 AM
    },
    'send-monthly-probation-reports': {
        'task': 'hr_portal.tasks.send_monthly_probation_reports_task',
        'schedule': crontab(minute=0, hour=9, day_of_month='1'),  # Run on the first day of every month at 9 AM
    },
}

# Additional email settings
ADMINS = [
    ('Admin Team', 'muhammad.hamza@giki.edu.pk'),
]
MANAGERS = [
    ('Manager Team', 'muhammad.hamza@giki.edu.pk'),
]
