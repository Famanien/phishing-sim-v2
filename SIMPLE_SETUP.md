# SIMPLE FIREBASE SETUP - No Installation Required!

## The Problem

Your Python 3.14 installation has configuration issues that prevent installing packages. 

## The Solution

**I'll create a standalone version that bundles Firebase dependencies directly in your project!**

This means:
- ✅ No pip required
- ✅ No package installation needed  
- ✅ Everything works out of the box

## What I'm Doing

Creating a `libs/` folder in your project with all Firebase dependencies included. Your app will use these local libraries instead of installed packages.

## Steps

1. I'll download the Firebase Admin SDK and its dependencies
2. Place them in a `libs/` folder in your project
3. Update the code to use the local libraries
4. You'll be ready to run!

## After Setup

Just run:
```bash
cd "c:\Users\Windows\Downloads\Automated Phishing Tool\phishing-sim-project"

# Copy credentials
copy "..\phishing-simulation-proj-2e16c-firebase-adminsdk-fbsvc-09a50f85e9.json" "firebase-credentials.json"

# Run your app
python backend/app.py
```

That's it! No installation needed.

---

**Alternative: Fix Your Python Installation**

If you want to fix Python 3.14 instead, you may need to:
1. Reinstall Python 3.14 from python.org
2. Make sure to check "Add Python to PATH" during installation
3. Or use an older Python version (3.11 or 3.12) which is more stable

But the bundled approach above will work immediately without fixing Python!
