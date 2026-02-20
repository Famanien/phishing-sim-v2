# Fix: Terminal Using Wrong Python Version

## Problem
You have both Python 3.14 (broken) and Python 3.12 (working) installed. Your terminal is defaulting to the broken 3.14.

## Solution: Uninstall Python 3.14

### Step 1: Uninstall Python 3.14

1. **Press Windows Key**
2. **Type:** "Add or remove programs"
3. **Press Enter**
4. **In the search box, type:** "Python"
5. **Find "Python 3.14"** in the list
6. **Click on it**
7. **Click "Uninstall"**
8. **Follow the prompts** to complete uninstallation

### Step 2: Verify Python 3.12 is Now Default

1. **Close ALL command prompt windows**
2. **Open a NEW command prompt**
3. **Type:**
   ```bash
   python --version
   ```
4. **You should now see:** `Python 3.12.x`

### Step 3: Install Flask and Run Your App

```bash
cd "c:\Users\Windows\Downloads\Automated Phishing Tool\phishing-sim-project"
pip install Flask Werkzeug
python backend\app.py
```

---

## Alternative: Use Python 3.12 Directly (Without Uninstalling)

If you don't want to uninstall 3.14 yet, you can use Python 3.12 directly:

```bash
# Use py launcher to specify version
py -3.12 --version

# Install Flask with Python 3.12
py -3.12 -m pip install Flask Werkzeug

# Run your app with Python 3.12
cd "c:\Users\Windows\Downloads\Automated Phishing Tool\phishing-sim-project"
py -3.12 backend\app.py
```

---

## Recommended: Uninstall 3.14

Since Python 3.14 is broken anyway, I recommend uninstalling it to avoid confusion. Then Python 3.12 will be your default.

After uninstalling 3.14 and verifying 3.12 works, your Firebase-integrated app will be ready to run!
