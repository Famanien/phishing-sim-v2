@echo off
echo ========================================
echo Phishing Simulation - Starting Server
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to tick "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -q Flask Werkzeug
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting Flask server...
echo.
echo Dashboard: http://localhost:5000
echo Training:  http://localhost:5000/training
echo Analytics: http://localhost:5000 (click Analytics in sidebar)
echo.
echo Press Ctrl+C to stop the server
echo.

python backend\app.py

pause
