# PythonAnywhere Deployment Steps

Follow these steps to deploy your HR Portal application to PythonAnywhere for free:

## Step 1: Create a PythonAnywhere Account
1. Go to https://www.pythonanywhere.com/
2. Click "Sign up" and create a free account
3. Verify your email address if prompted

## Step 2: Upload Your Project Files
There are several ways to upload your project:

### Option A: Using Git (Recommended)
1. On your local machine, make sure your project is in a Git repository
2. Create a public or private repository on GitHub/GitLab
3. On PythonAnywhere, open a Bash console (Consoles tab → Bash)
4. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   ```

### Option B: Direct Upload
1. Go to the Files tab on PythonAnywhere
2. Create a folder for your project (e.g., `hr_portal`)
3. Upload all your project files using the "Upload a file" button
4. You may need to zip your project first, upload the zip, then extract it

## Step 3: Create a Virtual Environment
1. Open a Bash console on PythonAnywhere
2. Create a virtual environment with Python 3.12:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.12 hrportal_env
   ```
3. Activate the virtual environment:
   ```bash
   workon hrportal_env
   ```

## Step 4: Install Dependencies
1. Navigate to your project directory:
   ```bash
   cd ~/hr_portal  # Replace with your project folder name
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Step 5: Configure Your Web App
1. Go to the "Web" tab on PythonAnywhere
2. Click "Add a new web app"
3. Select "Manual configuration (including virtualenvs)"
4. Choose Python 3.12
5. Complete the wizard

## Step 6: Configure Your Application Settings
In the Web tab, configure these settings:

### Code Section:
- Source code: `/home/yourusername/hr_portal` (replace with your actual path)
- Working directory: `/home/yourusername/hr_portal`

### Virtualenv Section:
- Path: `/home/yourusername/.virtualenvs/hrportal_env`

## Step 7: Set Environment Variables
In the Web tab, scroll down to "Environment variables" and add:

```
SECRET_KEY=your_very_long_random_secret_key_here_much_longer_than_this_example_key
DEBUG=False
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
OPENAI_API_KEY=your_openai_api_key_if_using_ai_features
```

To generate a good secret key, you can use:
```python
import secrets
print(secrets.token_urlsafe(50))
```

## Step 8: Configure Static Files
In the Web tab, in the "Static files" section, add:
- URL: `/static/`
- Directory: `/home/yourusername/hr_portal/staticfiles`

## Step 9: Run Setup Commands
1. Open a Bash console
2. Run these commands:
   ```bash
   workon hrportal_env
   cd ~/hr_portal  # Replace with your project directory
   
   # Run database migrations
   python manage.py migrate
   
   # Collect static files
   python manage.py collectstatic --noinput
   
   # Create a superuser account
   python manage.py createsuperuser
   ```
   
   When prompted for the superuser credentials:
   - Username: Enter your preferred username
   - Email: Enter your email address
   - Password: Enter a strong password (you'll enter it twice)

## Step 10: Reload Your Web App
1. Go back to the "Web" tab
2. Click the "Reload" button near the top of the page

## Step 11: Visit Your Site
1. Go back to the "Web" tab
2. Click on your domain name (it will look like `yourusername.pythonanywhere.com`)
3. You should see your HR Portal application running!

## Troubleshooting Tips

### If you get a "Disallowed Host" error:
Make sure your ALLOWED_HOSTS setting in settings.py includes your PythonAnywhere domain.

### If static files aren't loading:
- Verify that you ran `collectstatic`
- Check that your static files configuration is correct in the Web tab
- Ensure your STATIC_ROOT and STATIC_URL settings are properly configured

### If you get a database error:
- Make sure you ran `python manage.py migrate`
- Check that your database file has proper permissions

### If you need to make changes later:
1. Update your code locally
2. Upload the changes to PythonAnywhere (via Git or direct upload)
3. Run any new migrations: `python manage.py migrate`
4. Collect static files if you changed any: `python manage.py collectstatic`
5. Reload your web app in the Web tab

## Important Notes
- Free accounts on PythonAnywhere sleep after 30 minutes of inactivity
- Your application will restart when accessed after sleeping
- For production use, consider upgrading to a paid account for better performance and uptime
- Keep your API keys and passwords secure and never commit them to public repositories