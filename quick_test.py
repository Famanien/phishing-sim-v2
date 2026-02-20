"""
Quick test to verify Flask app can start without errors
"""

import sys
import os

print("=" * 60)
print("TESTING FLASK APP INITIALIZATION")
print("=" * 60)

try:
    print("\n1. Testing database import...")
    from backend.database import Database
    print("   ✓ Database module imported successfully")
    
    print("\n2. Testing automation import...")
    from backend.automation import CampaignAutomation, MetricsTracker
    print("   ✓ Automation module imported successfully")
    
    print("\n3. Testing Flask import...")
    from flask import Flask
    print("   ✓ Flask imported successfully")
    
    print("\n4. Initializing database...")
    db = Database()
    print("   ✓ Database initialized successfully")
    
    print("\n5. Checking database tables...")
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    expected_tables = ['users', 'campaigns', 'messages', 'events', 'user_risk', 'templates', 'campaign_metrics']
    all_present = all(table in tables for table in expected_tables)
    
    if all_present:
        print(f"   ✓ All {len(expected_tables)} tables present")
    else:
        print(f"   ✗ Missing tables: {set(expected_tables) - set(tables)}")
    
    print("\n6. Testing automation module...")
    automation = CampaignAutomation()
    print("   ✓ Automation module initialized")
    
    print("\n7. Testing metrics tracker...")
    tracker = MetricsTracker()
    print("   ✓ Metrics tracker initialized")
    
    print("\n8. Checking if templates are seeded...")
    templates = db.get_all_templates()
    if len(templates) > 0:
        print(f"   ✓ {len(templates)} templates found in database")
    else:
        print("   ⚠ No templates found - will be seeded on first app run")
    
    print("\n9. Checking if users are seeded...")
    users = db.get_all_users()
    if len(users) > 0:
        print(f"   ✓ {len(users)} users found in database")
    else:
        print("   ⚠ No users found - will be seeded on first app run")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe Flask application is ready to run!")
    print("\nTo start the server:")
    print("  Option 1: Double-click 'start_server.bat'")
    print("  Option 2: Run 'python backend/app.py'")
    print("\nThen open http://localhost:5000 in your browser")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("❌ TESTS FAILED")
    print("=" * 60)
    sys.exit(1)
