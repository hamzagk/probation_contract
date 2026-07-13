#!/bin/bash
# Startup script for HR Portal on PythonAnywhere

# Activate virtual environment
source /home/$PA_USERNAME/.virtualenvs/hrportal_env/bin/activate

# Navigate to project directory
cd $PA_BASE_PATH/mysite  # Adjust path as needed

# Install/update dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create a default superuser if none exists (optional)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Restart the web server
echo 'Restarting web server...'