"""
Quick test to verify Firebase setup
"""

# Test 1: Check if firebase-admin is installed
try:
    import firebase_admin
    print("✓ firebase-admin package is installed")
    print(f"  Version: {firebase_admin.__version__}")
except ImportError as e:
    print("✗ firebase-admin package is NOT installed")
    print(f"  Error: {e}")
    print("\n  To install, run: pip install firebase-admin")
    exit(1)

# Test 2: Check if credentials file exists
import os
cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
if os.path.exists(cred_path):
    print(f"✓ Firebase credentials file found at: {cred_path}")
else:
    print(f"✗ Firebase credentials file NOT found at: {cred_path}")
    print("\n  Please ensure the credentials file is in the project root directory")
    exit(1)

# Test 3: Try to import the Firebase database module
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from firebase_database import FirebaseDatabase
    print("✓ firebase_database module imported successfully")
except Exception as e:
    print(f"✗ Failed to import firebase_database module")
    print(f"  Error: {e}")
    exit(1)

# Test 4: Try to initialize Firebase
try:
    db = FirebaseDatabase()
    print("✓ Firebase database initialized successfully")
    print(f"  Database URL: {db.database_url}")
except Exception as e:
    print(f"✗ Failed to initialize Firebase database")
    print(f"  Error: {e}")
    exit(1)

print("\n" + "="*50)
print("ALL TESTS PASSED! Firebase is ready to use.")
print("="*50)
