# Firebase Setup - Manual Installation Required

## Issue Identified

Your Python installation doesn't have `pip` installed, which is preventing automatic package installation.

## Solution: Manual Installation Steps

### Option 1: Run the Manual Installer (Recommended)

I've created a script that will download and install firebase-admin without needing pip:

```bash
cd "c:\Users\Windows\Downloads\Automated Phishing Tool\phishing-sim-project"
python manual_install_firebase.py
```

This script will:
1. Download firebase-admin package directly from PyPI
2. Extract it to your Python packages directory
3. Verify the installation

### Option 2: Use a Different Python Installation

If you have another Python installation with pip:

```bash
# Check if you have py command
py --version

# If yes, use it to install:
py -m pip install firebase-admin
```

### Option 3: Install Pip First

```bash
# Download get-pip.py
python -c "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"

# Install pip
python get-pip.py

# Then install firebase-admin
python -m pip install firebase-admin
```

## After Installation

Once firebase-admin is installed, run:

```bash
# 1. Copy credentials file
copy "c:\Users\Windows\Downloads\Automated Phishing Tool\phishing-simulation-proj-2e16c-firebase-adminsdk-fbsvc-09a50f85e9.json" "c:\Users\Windows\Downloads\Automated Phishing Tool\phishing-sim-project\firebase-credentials.json"

# 2. Test the setup
python test_firebase_setup.py

# 3. Run your app
python backend/app.py
```

## Files Created

All Firebase integration files are ready:
- ✅ `backend/firebase_database.py` - Complete Firebase database module  
- ✅ `backend/__init__.py` - Updated to use Firebase
- ✅ `.gitignore` - Protects credentials
- ✅ `requirements.txt` - Lists firebase-admin dependency
- ✅ `test_firebase_setup.py` - Verification script
- ✅ `manual_install_firebase.py` - Manual installer
- ✅ `install_firebase.bat` - Batch installer with fallbacks

**The only thing left is installing the firebase-admin package!**

## Quick Command Reference

```bash
# Navigate to project
cd "c:\Users\Windows\Downloads\Automated Phishing Tool\phishing-sim-project"

# Try manual installer
python manual_install_firebase.py

# Or try installing pip first
python -c "import urllib.request; urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"
python get-pip.py
python -m pip install firebase-admin

# Copy credentials
copy "..\phishing-simulation-proj-2e16c-firebase-adminsdk-fbsvc-09a50f85e9.json" "firebase-credentials.json"

# Test
python test_firebase_setup.py

# Run app
python backend/app.py
```
