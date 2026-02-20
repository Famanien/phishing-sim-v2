# How to Install Python 3.12 on Windows

## Step-by-Step Installation Guide

### Step 1: Download Python

1. **Go to:** https://www.python.org/downloads/
2. **Click** the big yellow button that says **"Download Python 3.12.x"**
   - (The exact version might be 3.12.0, 3.12.1, 3.12.7, etc.)
3. **Save the file** (it will be named something like `python-3.12.x-amd64.exe`)

### Step 2: Run the Installer

1. **Double-click** the downloaded file
2. **CRITICAL:** At the bottom of the installer window, you'll see two checkboxes:
   
   ```
   ☐ Install launcher for all users (recommended)
   ☐ Add python.exe to PATH
   ```
   
   **✓ CHECK the "Add python.exe to PATH" box** ← This is VERY important!

3. **Click** "Install Now" (the big button at the top)

### Step 3: Wait for Installation

- The installer will show progress
- It should take 1-2 minutes
- You may see a Windows security prompt - click "Yes" to allow

### Step 4: Verify Installation

1. **Open a NEW Command Prompt** (important - must be new!)
   - Press `Windows Key + R`
   - Type `cmd`
   - Press Enter

2. **Type these commands to verify:**
   ```bash
   python --version
   ```
   You should see: `Python 3.12.x`

   ```bash
   pip --version
   ```
   You should see: `pip 24.x.x from ...`

### Step 5: Install Flask for Your Project

Once Python is installed, run these commands:

```bash
cd "c:\Users\Windows\Downloads\Automated Phishing Tool\phishing-sim-project"
pip install Flask Werkzeug
```

### Step 6: Run Your App!

```bash
python backend\app.py
```

Then open your browser to: **http://localhost:5000**

---

## Troubleshooting

### If "python" command not found:
- You forgot to check "Add python.exe to PATH"
- Solution: Uninstall Python and reinstall, making sure to check that box

### If you have Python 3.14 installed:
- Uninstall Python 3.14 first (it's broken)
- Then install Python 3.12

### To uninstall old Python:
1. Windows Settings → Apps
2. Find "Python 3.14"
3. Click "Uninstall"
4. Then install Python 3.12

---

## Why Python 3.12 Instead of 3.14?

- Python 3.12 is more stable
- Better package compatibility
- Your current 3.14 installation is broken
- 3.12 is the recommended version for production use

---

## After Installation

Once Python is working, your phishing simulation app will:
- ✅ Run with SQLite database (works immediately)
- ✅ Have all features working
- ✅ Be ready to add Firebase later (optional)

To add Firebase later:
```bash
pip install firebase-admin
copy "..\phishing-simulation-proj-2e16c-firebase-adminsdk-fbsvc-09a50f85e9.json" "firebase-credentials.json"
```

Then restart the app - it will automatically use Firebase!
