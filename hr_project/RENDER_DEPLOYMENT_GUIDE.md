# Render Deployment Guide

## Deploying the HR Portal to Render

### Prerequisites
- Render account (sign up at https://render.com)
- GitHub account (Render connects to GitHub for deployment)

### Steps to Deploy

1. **Sign Up/Log In to Render**
   - Go to https://render.com
   - Sign up or log in to your account

2. **Create a New Web Service**
   - Click "New +" and select "Web Service"
   - Connect to your GitHub repository containing the HR Portal

3. **Configure the Web Service**
   - **Name**: Choose a unique name for your application
   - **Environment**: Python
   - **Branch**: main or master (depending on your repository)
   
4. **Build Settings**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python manage.py migrate && gunicorn hr_project.wsgi:application`

5. **Environment Variables**
   - Click on "Advanced" to add environment variables:
     - `SECRET_KEY`: Generate a strong secret key
     - `DEBUG`: Set to `False` for production
     - `EMAIL_HOST_USER`: Your email address for sending notifications
     - `EMAIL_HOST_PASSWORD`: Your email app password
     - `ALLOWED_HOSTS`: Your render domain (e.g., `your-app-name.onrender.com`)

6. **Deploy**
   - Click "Create Web Service" to start the deployment process
   - Monitor the deployment logs in the dashboard

### Post-Deployment Steps

1. **Run Initial Setup**
   - After deployment, you may need to run initial setup commands
   - Use Render's dashboard to run: `python manage.py migrate`
   - Create a superuser: `python manage.py createsuperuser`

2. **Access Your Application**
   - Your application will be available at the URL provided by Render
   - Access the admin panel at `/admin/`
   - Main application at the root URL

### Environment Variables Reference

- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST_USER`: Email address for sending notifications
- `EMAIL_HOST_PASSWORD`: App password for email account
- `DATABASE_URL`: PostgreSQL database URL (if using Render's database)

### Health Check

- Render periodically checks your application health
- By default, it checks the root URL (`/`)
- If you need a custom health check endpoint, configure it in the settings

### Troubleshooting

- If you encounter issues with static files, make sure to run `collectstatic` after deployment
- Check logs regularly for any errors during deployment or runtime
- Ensure all required environment variables are set correctly

### Scaling

- Render allows you to scale your application based on traffic needs
- Adjust instance size in the dashboard as needed
- Consider using Render's PostgreSQL add-on for production databases