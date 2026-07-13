# GitHub Deployment Guide

## How to Deploy the HR Portal to GitHub and Connect to Deployment Platforms

### Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Sign in to your account
3. Click the "+" icon in the top right corner and select "New repository"
4. Give your repository a name (e.g., "gik-hr-portal")
5. Add a description
6. Choose "Public" or "Private" as per your preference
7. Check "Add a README file"
8. Select "None" for .gitignore (we already have one)
9. Select "MIT License" or your preferred license
10. Click "Create repository"

### Step 2: Initialize Git Locally and Connect to GitHub

Open your terminal/command prompt in the project directory and run:

```bash
# Initialize git in your project folder
git init

# Add all files to git
git add .

# Commit the files
git commit -m "Initial commit: GIK Institute HR Portal"

# Add the GitHub repository as origin
git remote add origin https://github.com/YOUR_USERNAME/gik-hr-portal.git

# Push the code to GitHub
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 3: Connect to Deployment Platforms

#### Option A: Deploy to Render

1. Go to [https://render.com](https://render.com)
2. Sign up or log in
3. Click "New +" and select "Web Service"
4. Click "Connect to GitHub"
5. Select your repository (gik-hr-portal)
6. Configure the settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python manage.py migrate && gunicorn hr_project.wsgi:application`
7. Add environment variables in the "Advanced" section
8. Click "Create Web Service"

#### Option B: Deploy to Railway

1. Go to [https://railway.app](https://railway.app)
2. Sign up or log in
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Configure the settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python manage.py migrate && gunicorn hr_project.wsgi:application`
7. Add environment variables in the "Variables" section
8. Click "Deploy Now"

#### Option C: Deploy to Heroku

1. Go to [https://heroku.com](https://heroku.com)
2. Sign up or log in
3. Click "New" and select "Create new app"
4. Give your app a name and select a region
5. Go to the "Deploy" tab
6. Select "GitHub" as deployment method
7. Connect to your GitHub account
8. Search for your repository and connect it
9. Go to the "Settings" tab
10. Add buildpack: `heroku/python`
11. Go to the "Deploy" tab
12. Click "Enable Automatic Deploys" (optional)
13. Click "Deploy Branch" for manual deployment

### Step 4: Set Environment Variables

For all platforms, you'll need to set these environment variables:

- `SECRET_KEY`: Generate a strong secret key (use Django's secret key generator)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Set to your deployment URL (e.g., `your-app.herokuapp.com`)
- `EMAIL_HOST_USER`: Your email address for sending notifications
- `EMAIL_HOST_PASSWORD`: Your email app password
- `DATABASE_URL`: If using platform's database service

### Step 5: Run Initial Setup

After deployment, you may need to run initial setup commands:

1. For database migrations: `python manage.py migrate`
2. To create a superuser: `python manage.py createsuperuser`

Some platforms allow running these commands in their console, others may require you to run them locally with the production database.

### Step 6: Verify Deployment

1. Visit your deployed application URL
2. Check that all pages load correctly
3. Test employee management functionality
4. Verify email notifications work
5. Ensure all GIK Institute departments appear in the dropdown

### Troubleshooting Common Issues

1. **Application won't start**: Check logs for error messages
2. **Static files not loading**: Ensure `collectstatic` ran correctly
3. **Database errors**: Verify migrations ran successfully
4. **Email not working**: Check email configuration and app passwords
5. **Permission errors**: Verify all required environment variables are set

### Maintaining Your Deployment

1. **Push updates**: Changes pushed to GitHub will automatically deploy if you enabled automatic deploys
2. **Monitor logs**: Check platform logs for errors
3. **Backup data**: Regularly backup your database
4. **Update dependencies**: Periodically update packages in requirements.txt
5. **Security updates**: Keep Django and other packages updated

### Best Practices

1. Never commit sensitive information to GitHub
2. Use environment variables for all secrets
3. Keep your requirements.txt updated
4. Test changes locally before pushing to production
5. Monitor application performance
6. Set up alerts for downtime or errors