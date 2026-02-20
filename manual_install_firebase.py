"""
Manual Firebase Admin SDK installer
Downloads and installs firebase-admin without using pip
"""

import sys
import os
import urllib.request
import zipfile
import shutil
from pathlib import Path

print("=" * 60)
print("Firebase Admin SDK Manual Installer")
print("=" * 60)
print()

# Check Python version
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

# Get site-packages directory
site_packages = None
for path in sys.path:
    if 'site-packages' in path.lower() and os.path.exists(path):
        site_packages = path
        break

if not site_packages:
    # Create a local packages directory
    site_packages = os.path.join(os.path.dirname(__file__), 'packages')
    os.makedirs(site_packages, exist_ok=True)
    sys.path.insert(0, site_packages)
    print(f"Created local packages directory: {site_packages}")
else:
    print(f"Using site-packages: {site_packages}")

print()
print("Downloading firebase-admin package...")
print("This may take a moment...")
print()

# Download firebase-admin wheel file
url = "https://files.pythonhosted.org/packages/py3/f/firebase-admin/firebase_admin-6.3.0-py3-none-any.whl"
wheel_file = "firebase_admin-6.3.0-py3-none-any.whl"

try:
    urllib.request.urlretrieve(url, wheel_file)
    print(f"✓ Downloaded {wheel_file}")
except Exception as e:
    print(f"✗ Failed to download: {e}")
    print()
    print("Alternative: Download manually from:")
    print("https://pypi.org/project/firebase-admin/#files")
    sys.exit(1)

# Extract wheel file (it's just a zip)
print()
print("Extracting package...")

try:
    with zipfile.ZipFile(wheel_file, 'r') as zip_ref:
        zip_ref.extractall(site_packages)
    print(f"✓ Extracted to {site_packages}")
except Exception as e:
    print(f"✗ Failed to extract: {e}")
    sys.exit(1)

# Clean up
os.remove(wheel_file)
print("✓ Cleaned up temporary files")

# Verify installation
print()
print("Verifying installation...")
try:
    import firebase_admin
    print(f"✓ firebase-admin successfully installed!")
    print(f"  Version: {firebase_admin.__version__}")
except ImportError as e:
    print(f"✗ Installation verification failed: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("Installation Complete!")
print("=" * 60)
print()
print("Note: This package was installed locally.")
print(f"Location: {site_packages}")
print()
print("You can now run: python test_firebase_setup.py")
