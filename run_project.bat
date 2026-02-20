@echo off
echo Starting Phishing Simulation Project...
echo.

cd /d "%~dp0"

echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python.
    pause
    exit /b
)

echo.
echo Installing requirements (if needed)...
python -m pip install -r requirements.txt

echo.
echo Starting Flask Server...
echo Access the dashboard at: http://127.0.0.1:5000
echo Access the phishing simulation at: http://127.0.0.1:5000/login
echo.

set FLASK_APP=backend/app.py
set FLASK_ENV=development
python -m flask run

pause
