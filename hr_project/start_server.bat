@echo off
echo Starting GIK Institute HR Portal...

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Install dependencies if not already installed
pip install -r requirements.txt

REM Run migrations
python manage.py migrate

REM Start the development server
echo Starting development server on http://127.0.0.1:8000/
python manage.py runserver 8000