@echo off
echo Installing Firebase Admin SDK...
echo.

REM Try different methods to install firebase-admin

echo Method 1: Using python -m pip
python -m pip install firebase-admin
if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Firebase Admin SDK installed successfully.
    goto :verify
)

echo.
echo Method 1 failed. Trying Method 2...
echo.

echo Method 2: Using py -m pip
py -m pip install firebase-admin
if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Firebase Admin SDK installed successfully.
    goto :verify
)

echo.
echo Method 2 failed. Trying Method 3...
echo.

echo Method 3: Direct pip3
pip3 install firebase-admin
if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Firebase Admin SDK installed successfully.
    goto :verify
)

echo.
echo All methods failed. Please install manually with:
echo   python -m pip install --user firebase-admin
echo.
pause
exit /b 1

:verify
echo.
echo Verifying installation...
python -c "import firebase_admin; print('Firebase Admin SDK version:', firebase_admin.__version__)"
echo.
echo Installation complete!
echo.
pause
