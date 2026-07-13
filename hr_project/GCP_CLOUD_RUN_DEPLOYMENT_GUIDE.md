# Google Cloud Platform (GCP) Cloud Run Deployment Guide

## Deploying the HR Portal to GCP Cloud Run

### Prerequisites
- Google Cloud Platform account with billing enabled
- Google Cloud SDK installed locally
- Docker installed locally

### Steps to Deploy

1. **Set Up Your GCP Project**
   - Create a new project in the Google Cloud Console
   - Enable the Cloud Run API
   - Enable the Container Registry API

2. **Install and Configure Google Cloud SDK**
   ```bash
   # Download and install Google Cloud SDK
   # Authenticate with your Google account
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Prepare Your Application**
   - Ensure your application is configured to run on port 8080 (Cloud Run requirement)
   - Create a Dockerfile in your project root:

   ```dockerfile
   FROM python:3.12-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   # Install gunicorn if not in requirements
   RUN pip install gunicorn
   
   # Expose port 8080
   EXPOSE 8080
   
   # Run the application
   CMD ["gunicorn", "--bind", "0.0.0.0:8080", "hr_project.wsgi:application"]
   ```

4. **Build and Push Docker Image**
   ```bash
   # Build the Docker image
   docker build -t gcr.io/YOUR_PROJECT_ID/hr-portal .
   
   # Push the image to Google Container Registry
   docker push gcr.io/YOUR_PROJECT_ID/hr-portal
   ```

5. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy hr-portal \
     --image gcr.io/YOUR_PROJECT_ID/hr-portal \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars SECRET_KEY="your-secret-key",DEBUG=False,EMAIL_HOST_USER="your-email",EMAIL_HOST_PASSWORD="your-password",ALLOWED_HOSTS="*"
   ```

6. **Alternative: Deploy Using Cloud Console**
   - Go to Cloud Run in the Google Cloud Console
   - Click "Create Service"
   - Select "Deploy one revision from an existing container image"
   - Enter your image URL: `gcr.io/YOUR_PROJECT_ID/hr-portal`
   - Configure the service settings:
     - Service name: hr-portal
     - Region: Select your preferred region
     - Authentication: Allow unauthenticated invocations (or restrict as needed)
     - Memory allocated: 512MB (adjust as needed)
     - CPU allocated: 1 vCPU
   - Add environment variables:
     - SECRET_KEY: Your Django secret key
     - DEBUG: False
     - EMAIL_HOST_USER: Your email address
     - EMAIL_HOST_PASSWORD: Your email app password
     - ALLOWED_HOSTS: Your Cloud Run URL

### Post-Deployment Steps

1. **Run Initial Setup**
   - Connect to your deployed instance or run setup commands in the container
   - Run database migrations: `python manage.py migrate`
   - Create a superuser: `python manage.py createsuperuser`

2. **Configure Domain (Optional)**
   - In Cloud Run console, go to "Custom domains"
   - Add your custom domain and follow the verification process

### Environment Variables Reference

- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST_USER`: Email address for sending notifications
- `EMAIL_HOST_PASSWORD`: App password for email account
- `DATABASE_URL`: PostgreSQL database URL (if using Cloud SQL)

### Using Cloud SQL (Recommended for Production)

For production deployments, consider using Cloud SQL for your database:

1. Create a Cloud SQL instance (PostgreSQL or MySQL)
2. Update your settings.py to use the Cloud SQL database
3. Set the `DATABASE_URL` environment variable to your Cloud SQL connection string

### Troubleshooting

- Check Cloud Run logs in the Google Cloud Console for any errors
- Ensure your application listens on port 8080
- Verify all required environment variables are set
- Check that your firewall rules allow connections

### Scaling

- Cloud Run automatically scales based on demand
- Configure min/max instances in the Cloud Run settings if needed
- Monitor resource usage in Cloud Monitoring