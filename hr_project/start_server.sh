#!/bin/bash

echo "Starting GIK Institute HR Portal..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate  # Linux/Mac
    # For Windows use: venv\Scripts\activate
fi

# Install dependencies if not already installed
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the development server
echo "Starting development server on http://127.0.0.1:8000/"
python manage.py runserver 8000