@echo off
echo ====================================
echo  Starting Pridicto Backend (Django)
echo ====================================

cd /d "%~dp0backend"

if not exist ".env" (
    copy .env.example .env
    echo [!] Created .env from .env.example — please fill in your API keys!
)

if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [*] Installing dependencies...
pip install -r requirements.txt --quiet

echo [*] Running migrations...
python manage.py migrate --run-syncdb

echo [*] Starting Django on http://localhost:8000 ...
python manage.py runserver
