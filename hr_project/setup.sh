#!/bin/bash
# Deployment setup script

echo "Setting up HR Portal for deployment..."

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py collectstatic --noinput
python manage.py migrate

echo "Setup complete! Your application is ready for deployment."