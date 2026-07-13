@echo off
cd /d "C:\Users\Hamza\.qwen\projects\hr_project"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the automatic email notifications
python manage.py run_automatic_emails

pause