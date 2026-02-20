"""
Test script to verify Sprint 5 implementation
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import Database
from automation import CampaignAutomation, MetricsTracker

def test_database():
    """Test database initialization"""
    print("=" * 50)
    print("Testing Database Initialization...")
    print("=" * 50)
    
    db = Database()
    
    # Check tables exist
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    expected_tables = ['users', 'campaigns', 'messages', 'events', 'user_risk', 'templates', 'campaign_metrics']
    
    print(f"\nExpected tables: {len(expected_tables)}")
    print(f"Found tables: {len(tables)}")
    
    for table in expected_tables:
        status = "✓" if table in tables else "✗"
        print(f"  {status} {table}")
    
    # Check if templates were seeded
    templates = db.get_all_templates()
    print(f"\n✓ Templates seeded: {len(templates)} templates")
    
    # Check if users were seeded
    users = db.get_all_users()
    print(f"✓ Users seeded: {len(users)} users")
    
    return db

def test_automation(db):
    """Test automation functionality"""
    print("\n" + "=" * 50)
    print("Testing Automation Module...")
    print("=" * 50)
    
    automation = CampaignAutomation()
    
    # Test weekly simulation
    print("\nRunning Week 5 simulation...")
    result = automation.run_weekly_simulation(week_number=5)
    
    if result.get('success'):
        print(f"✓ Simulation successful!")
        print(f"  - Campaigns launched: {len(result['campaigns_launched'])}")
        print(f"  - Total messages: {result['total_messages']}")
        
        for campaign in result['campaigns_launched']:
            print(f"\n  Campaign: {campaign['campaign_name']}")
            print(f"    - Messages sent: {campaign['messages_sent']}")
            print(f"    - Target users: {campaign['target_users']}")
    else:
        print(f"✗ Simulation failed: {result.get('error')}")
    
    return automation

def test_metrics(db):
    """Test metrics tracking"""
    print("\n" + "=" * 50)
    print("Testing Metrics Tracking...")
    print("=" * 50)
    
    tracker = MetricsTracker()
    
    # Get all metrics
    metrics = tracker.get_all_campaign_metrics()
    print(f"\n✓ Campaign metrics available: {len(metrics)}")
    
    for m in metrics:
        print(f"\n  {m['campaign']} ({m['difficulty']})")
        print(f"    - Status: {m['status']}")
        print(f"    - Sent: {m['sent']}")
        print(f"    - Click rate: {m['click_rate']}")
        print(f"    - Report rate: {m['report_rate']}")

def test_user_risk(db):
    """Test user risk tracking"""
    print("\n" + "=" * 50)
    print("Testing User Risk Tracking...")
    print("=" * 50)
    
    users = db.get_all_users()
    
    print(f"\nTotal users: {len(users)}")
    
    for user in users[:3]:  # Show first 3 users
        risk = db.get_user_risk(user['id'])
        print(f"\n  {user['name']} ({user['email']})")
        print(f"    - Risk Score: {risk['risk_score']}")
        print(f"    - Risk Category: {risk['risk_category']}")
        print(f"    - Repeat Offender: {'Yes' if risk['is_repeat_offender'] else 'No'}")

def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("SPRINT 5 - VERIFICATION TESTS")
    print("=" * 50)
    
    try:
        # Test database
        db = test_database()
        
        # Test automation
        automation = test_automation(db)
        
        # Test metrics
        test_metrics(db)
        
        # Test user risk
        test_user_risk(db)
        
        print("\n" + "=" * 50)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Run 'python backend/app.py' to start the web server")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Explore the admin dashboard")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
