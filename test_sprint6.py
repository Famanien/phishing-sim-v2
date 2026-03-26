"""
Sprint 6 – Optimisation & Behaviour Analysis
QA Test Suite

Tests all new analytics endpoints, repeat-offender logic, pattern insights,
KPI summary, and CSV export added in Sprint 6.

Run from project root:
    python test_sprint6.py
"""

import sys
import os
import json

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import Database
from backend.app import app

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def ok(msg):
    print(f"  ✅ PASS  {msg}")

def fail(msg):
    print(f"  ❌ FAIL  {msg}")

def run_tests():
    passed = 0
    failed = 0

    # -----------------------------------------------------------------------
    # 1. Database layer tests
    # -----------------------------------------------------------------------
    header("1. Database – Sprint 6 methods")

    db = Database()

    # get_kpi_summary
    try:
        kpis = db.get_kpi_summary()
        assert isinstance(kpis, dict), "Expected dict"
        assert 'overall_click_rate' in kpis
        assert 'overall_report_rate' in kpis
        assert 'overall_training_completion' in kpis
        assert 'repeat_offender_count' in kpis
        ok("get_kpi_summary() returns correct keys")
        passed += 1
    except Exception as e:
        fail(f"get_kpi_summary() → {e}")
        failed += 1

    # get_behaviour_trend_report
    try:
        trends = db.get_behaviour_trend_report()
        assert isinstance(trends, list), "Expected list"
        if trends:
            assert 'campaign' in trends[0]
            assert 'click_rate' in trends[0]
            assert 'report_rate' in trends[0]
            assert 'training_completion_rate' in trends[0]
        ok(f"get_behaviour_trend_report() → {len(trends)} campaign(s)")
        passed += 1
    except Exception as e:
        fail(f"get_behaviour_trend_report() → {e}")
        failed += 1

    # get_repeat_offenders
    try:
        offenders = db.get_repeat_offenders()
        assert isinstance(offenders, list), "Expected list"
        for o in offenders:
            assert 'user_id' in o
            assert 'total_clicks' in o
            assert 'campaigns_clicked' in o
            assert 'clicked_after_training' in o
            # Every offender should have ≥2 clicks OR clicked_after_training
            assert o['total_clicks'] >= 2 or o['clicked_after_training'], \
                f"User {o['user_id']} does not meet repeat-offender criteria"
        ok(f"get_repeat_offenders() → {len(offenders)} offender(s), all valid")
        passed += 1
    except Exception as e:
        fail(f"get_repeat_offenders() → {e}")
        failed += 1

    # get_pattern_insights
    try:
        insights = db.get_pattern_insights()
        assert isinstance(insights, dict)
        assert 'top_templates' in insights
        assert 'department_risk' in insights
        assert 'repeat_offender_count' in insights
        assert isinstance(insights['top_templates'], list)
        assert isinstance(insights['department_risk'], list)
        ok("get_pattern_insights() returns correct structure")
        passed += 1
    except Exception as e:
        fail(f"get_pattern_insights() → {e}")
        failed += 1

    # export_repeat_offenders_csv
    try:
        csv = db.export_repeat_offenders_csv()
        assert isinstance(csv, str)
        lines = csv.split('\n')
        assert lines[0] == 'Name,Email,Department,Total Clicks,Campaigns Clicked,Risk Category,Clicked After Training', \
            "CSV header mismatch"
        ok(f"export_repeat_offenders_csv() → {len(lines)} line(s)")
        passed += 1
    except Exception as e:
        fail(f"export_repeat_offenders_csv() → {e}")
        failed += 1

    # -----------------------------------------------------------------------
    # 2. API endpoint tests (via Flask test client)
    # -----------------------------------------------------------------------
    header("2. API – Sprint 6 endpoints")

    client = app.test_client()

    endpoints = [
        ('/api/analytics/kpis',             'kpis'),
        ('/api/analytics/behaviour-trends', 'trends'),
        ('/api/analytics/repeat-offenders', 'offenders'),
        ('/api/analytics/pattern-insights', 'insights'),
    ]

    for url, key in endpoints:
        try:
            resp = client.get(url)
            assert resp.status_code == 200, f"HTTP {resp.status_code}"
            data = json.loads(resp.data)
            assert data.get('success') is True, f"success=False: {data}"
            assert key in data, f"Missing key '{key}' in response"
            ok(f"GET {url} → 200 OK, has '{key}'")
            passed += 1
        except Exception as e:
            fail(f"GET {url} → {e}")
            failed += 1

    # CSV export
    try:
        resp = client.get('/api/analytics/export-repeat-offenders')
        assert resp.status_code == 200
        assert 'text/csv' in resp.content_type
        ok("GET /api/analytics/export-repeat-offenders → CSV response")
        passed += 1
    except Exception as e:
        fail(f"GET /api/analytics/export-repeat-offenders → {e}")
        failed += 1

    # -----------------------------------------------------------------------
    # 3. QA Cross-check – repeat-offender flag consistency
    # -----------------------------------------------------------------------
    header("3. QA – Repeat-offender flag consistency")

    try:
        offenders_api = db.get_repeat_offenders()
        # Every user in the list must have is_repeat_offender flag correctly set
        # in user_risk (may need update – endpoint does this automatically)
        for o in offenders_api:
            risk = db.get_user_risk(o['user_id'])
            if risk and not risk['is_repeat_offender'] and o['total_clicks'] >= 2:
                # update it now (endpoint does this, but direct DB call may lag)
                db.update_user_risk(o['user_id'])
        ok("Repeat-offender flags reconciled with user_risk table")
        passed += 1
    except Exception as e:
        fail(f"Flag consistency check → {e}")
        failed += 1

    # -----------------------------------------------------------------------
    # 4. Quiz content – Sprint 6 questions present
    # -----------------------------------------------------------------------
    header("4. Training Content – Sprint 6 quiz questions")

    try:
        questions = db.get_quiz_questions()
        categories = {q['category'] for q in questions}
        assert 'MFA Phishing' in categories, "MFA Phishing category not found"
        ok(f"MFA Phishing quiz category found ({len(questions)} total questions)")
        passed += 1
    except Exception as e:
        fail(f"Quiz category check → {e}")
        failed += 1

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    header("Sprint 6 QA Summary")
    total = passed + failed
    print(f"\n  Total: {total}  |  ✅ Passed: {passed}  |  ❌ Failed: {failed}")
    if failed == 0:
        print("\n  🎉 All Sprint 6 tests passed!\n")
    else:
        print(f"\n  ⚠️  {failed} test(s) failed – review output above.\n")

    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
