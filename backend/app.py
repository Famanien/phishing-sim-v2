"""
Flask Web Application for Phishing Simulation Admin Dashboard
Provides campaign management, metrics tracking, and automation controls
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Database
from backend.automation import CampaignAutomation, MetricsTracker

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Initialize components
db = Database()
automation = CampaignAutomation()
metrics_tracker = MetricsTracker()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get all campaigns"""
    campaigns = db.get_all_campaigns()
    return jsonify({'success': True, 'campaigns': campaigns})


@app.route('/api/campaigns/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get specific campaign details"""
    campaign = db.get_campaign(campaign_id)
    if not campaign:
        return jsonify({'success': False, 'error': 'Campaign not found'}), 404
    
    metrics = db.get_campaign_metrics(campaign_id)
    events = db.get_campaign_events(campaign_id)
    
    return jsonify({
        'success': True,
        'campaign': campaign,
        'metrics': metrics,
        'events': events
    })


@app.route('/api/campaigns/create', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    data = request.json
    
    campaign_id = db.create_campaign(
        name=data.get('name'),
        difficulty=data.get('difficulty', 'Easy'),
        template_id=data.get('template_id'),
        start_date=data.get('start_date'),
        target_segment=data.get('target_segment', 'all')
    )
    
    return jsonify({'success': True, 'campaign_id': campaign_id})


@app.route('/api/campaigns/<int:campaign_id>/launch', methods=['POST'])
def launch_campaign(campaign_id):
    """Launch a campaign"""
    result = automation.launch_campaign(campaign_id)
    return jsonify(result)


@app.route('/api/campaigns/<int:campaign_id>/complete', methods=['POST'])
def complete_campaign(campaign_id):
    """Mark campaign as completed"""
    automation.complete_campaign(campaign_id)
    return jsonify({'success': True})


@app.route('/api/automation/run-weekly', methods=['POST'])
def run_weekly_simulation():
    """
    Main automation trigger: Run weekly simulation
    This is the manual trigger that simulates automated scheduling
    """
    data = request.json
    week_number = data.get('week_number', 5)
    
    result = automation.run_weekly_simulation(week_number)
    return jsonify(result)


@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users with risk information"""
    users = db.get_all_users()
    
    # Enrich with risk data
    for user in users:
        risk_info = db.get_user_risk(user['id'])
        if risk_info:
            user['risk_score'] = risk_info['risk_score']
            user['risk_category'] = risk_info['risk_category']
            user['is_repeat_offender'] = risk_info['is_repeat_offender']
    
    return jsonify({'success': True, 'users': users})


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details with events and risk"""
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    events = db.get_user_events(user_id)
    risk = db.get_user_risk(user_id)
    
    return jsonify({
        'success': True,
        'user': user,
        'events': events,
        'risk': risk
    })


@app.route('/api/users/create', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.json
    
    user_id = db.add_user(
        email=data.get('email'),
        name=data.get('name'),
        department=data.get('department')
    )
    
    return jsonify({'success': True, 'user_id': user_id})


@app.route('/api/events/log', methods=['POST'])
def log_event():
    """Log a user event (click, report, etc.)"""
    data = request.json
    
    event_id = db.log_event(
        message_id=data.get('message_id'),
        user_id=data.get('user_id'),
        campaign_id=data.get('campaign_id'),
        event_type=data.get('event_type'),
        metadata=data.get('metadata')
    )
    
    # Update user risk after logging event
    db.update_user_risk(data.get('user_id'))
    
    return jsonify({'success': True, 'event_id': event_id})


@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all phishing templates"""
    templates = db.get_all_templates()
    return jsonify({'success': True, 'templates': templates})


@app.route('/api/templates/create', methods=['POST'])
def create_template():
    """Create a new phishing template"""
    data = request.json
    
    template_id = db.add_template(
        name=data.get('name'),
        difficulty=data.get('difficulty', 'Easy'),
        subject=data.get('subject'),
        sender_name=data.get('sender_name'),
        sender_email=data.get('sender_email'),
        body_content=data.get('body_content'),
        link_text=data.get('link_text')
    )
    
    return jsonify({'success': True, 'template_id': template_id})


@app.route('/api/metrics/all', methods=['GET'])
def get_all_metrics():
    """Get metrics for all campaigns"""
    metrics = metrics_tracker.get_all_campaign_metrics()
    return jsonify({'success': True, 'metrics': metrics})


@app.route('/api/metrics/trends', methods=['GET'])
def get_trends():
    """Get trend comparison data"""
    trends = metrics_tracker.get_trend_comparison()
    return jsonify({'success': True, 'trends': trends})


@app.route('/api/metrics/campaign/<int:campaign_id>', methods=['GET'])
def get_campaign_metrics(campaign_id):
    """Get detailed metrics for a specific campaign"""
    summary = metrics_tracker.get_campaign_summary(campaign_id)
    return jsonify({'success': True, 'summary': summary})


@app.route('/api/risk/users/<category>', methods=['GET'])
def get_users_by_risk(category):
    """Get users by risk category"""
    # Capitalize category properly
    category = category.capitalize()
    users = db.get_users_by_risk_category(category)
    return jsonify({'success': True, 'category': category, 'users': users})


@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get overall dashboard statistics"""
    users = db.get_all_users()
    campaigns = db.get_all_campaigns()
    all_metrics = db.get_all_metrics()
    
    # Calculate aggregate stats
    total_users = len(users)
    total_campaigns = len(campaigns)
    active_campaigns = len([c for c in campaigns if c['status'] == 'active'])
    
    # Risk distribution
    high_risk = len(db.get_users_by_risk_category('High'))
    medium_risk = len(db.get_users_by_risk_category('Medium'))
    low_risk = len(db.get_users_by_risk_category('Low'))
    
    # Average metrics
    if all_metrics:
        avg_click_rate = sum(m['click_rate'] for m in all_metrics) / len(all_metrics)
        avg_report_rate = sum(m['report_rate'] for m in all_metrics) / len(all_metrics)
    else:
        avg_click_rate = 0
        avg_report_rate = 0
    
    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'risk_distribution': {
                'high': high_risk,
                'medium': medium_risk,
                'low': low_risk
            },
            'average_click_rate': round(avg_click_rate, 2),
            'average_report_rate': round(avg_report_rate, 2)
        }
    })


@app.route('/login')
def login():
    """Phishing simulation landing page"""
    return render_template('login.html')


@app.route('/training')
def training():
    """Training and education page"""
    return render_template('dashboard.html')  # Redirect to dashboard as it's now integrated


@app.route('/api/quiz/questions', methods=['GET'])
def get_quiz_questions_api():
    """Get quiz questions"""
    questions = db.get_quiz_questions()
    return jsonify({'success': True, 'questions': questions})


@app.route('/api/quiz/submit', methods=['POST'])
def submit_quiz_answer_api():
    """Submit a quiz answer"""
    data = request.json
    user_id = data.get('user_id')
    question_id = data.get('question_id')
    selected_answer = data.get('selected_answer')
    
    if not all([user_id, question_id, selected_answer]):
        return jsonify({'success': False, 'error': 'Missing data'}), 400
        
    result = db.submit_quiz_answer(user_id, question_id, selected_answer)
    return jsonify({'success': True, 'result': result})


@app.route('/api/quiz/stats/<int:user_id>', methods=['GET'])
def get_user_quiz_stats_api(user_id):
    """Get quiz statistics for a user"""
    stats = db.get_user_quiz_stats(user_id)
    return jsonify({'success': True, 'stats': stats})



# Initialize database and seed data if needed
def initialize():
    """Initialize database on startup"""
    # Check if we need to seed initial data
    templates = db.get_all_templates()
    if not templates:
        print("Seeding initial templates...")
        seed_initial_data()



def seed_initial_data():
    """Seed database with initial templates and sample users"""
    # Add templates from Sprint 4 requirements
    
    # Easy templates (from existing docs)
    db.add_template(
        name="Password Reset",
        difficulty="Easy",
        subject="Action Required: Password Expiry Notification",
        sender_name="IT Support Team",
        sender_email="support@company-it.com",
        body_content="Dear User,\n\nYour account password is due to expire today. Failure to reset your password may result in temporary account suspension.\n\nPlease verify your account by clicking the link below.\n\n[LINK]\n\nIT Support Team",
        link_text="Reset Password"
    )
    
    # Medium templates
    db.add_template(
        name="Invoice Payment Request",
        difficulty="Medium",
        subject="Outstanding Invoice – Immediate Attention Required",
        sender_name="Accounts Team",
        sender_email="billing@accounts-dept.com",
        body_content="Hello,\n\nPlease find attached the outstanding invoice for recent services. Payment is required within 24 hours to avoid disruption.\n\nReview invoice here:\n[LINK]\n\nAccounts Team",
        link_text="View Invoice"
    )
    
    db.add_template(
        name="MFA Security Alert",
        difficulty="Medium",
        subject="Security Alert: Unusual Login Detected",
        sender_name="Security Operations",
        sender_email="security@company-alerts.com",
        body_content="Dear User,\n\nWe detected an unusual login attempt to your account from an unrecognized device.\n\nIf this was you, please verify your identity immediately. If not, secure your account now.\n\n[LINK]\n\nSecurity Operations Center",
        link_text="Verify Identity"
    )
    
    # Hard templates
    db.add_template(
        name="HR Policy Update",
        difficulty="Hard",
        subject="Updated HR Policy – Review Required",
        sender_name="Human Resources",
        sender_email="hr@company-portal.com",
        body_content="Dear Employee,\n\nHR policies have been updated in line with recent organisational changes. Please review the updated document below.\n\n[LINK]\n\nHuman Resources",
        link_text="Access HR Document"
    )
    
    db.add_template(
        name="Shared Document Access",
        difficulty="Hard",
        subject="Document Shared: Q1 Financial Report",
        sender_name="Sarah Mitchell",
        sender_email="s.mitchell@company.com",
        body_content="Hi,\n\nI've shared the Q1 financial report with you. Please review before tomorrow's meeting.\n\nAccess the document here:\n[LINK]\n\nBest regards,\nSarah Mitchell\nFinance Director",
        link_text="Open Document"
    )
    
    # Add sample users
    db.add_user("john.doe@company.com", "John Doe", "IT")
    db.add_user("jane.smith@company.com", "Jane Smith", "Finance")
    db.add_user("bob.jones@company.com", "Bob Jones", "HR")
    db.add_user("alice.williams@company.com", "Alice Williams", "Marketing")
    db.add_user("charlie.brown@company.com", "Charlie Brown", "Sales")
    
    print("Initial data seeded successfully!")


def seed_quiz_questions():
    """Seed database with educational quiz questions"""
    questions = db.get_quiz_questions(limit=1)
    if questions:
        return  # Already seeded
    
    print("Seeding quiz questions...")
    
    # Email Red Flags
    db.add_quiz_question(
        question="What is the MOST reliable way to verify if an email is legitimate?",
        option_a="Check if the email has a professional logo",
        option_b="Verify the sender's email address matches the official domain",
        option_c="See if the email uses proper grammar",
        option_d="Check if there are images in the email",
        correct_answer="B",
        explanation="Always verify the sender's email domain. Attackers can copy logos and use good grammar, but they cannot send from official company domains without access.",
        category="Email Red Flags",
        difficulty="Easy"
    )
    
    db.add_quiz_question(
        question="Which of these is a common sign of a phishing email?",
        option_a="The email is addressed to you by name",
        option_b="The email creates a sense of urgency or fear",
        option_c="The email has a company signature",
        option_d="The email is sent during business hours",
        correct_answer="B",
        explanation="Phishing emails often create urgency ('Your account will be closed!') or fear to pressure you into acting quickly without thinking.",
        category="Email Red Flags",
        difficulty="Easy"
    )
    
    db.add_quiz_question(
        question="You receive an email from 'support@amaz0n.com' asking you to verify your account. What should you notice?",
        option_a="The email is from Amazon support",
        option_b="The domain uses a zero (0) instead of the letter 'o'",
        option_c="The email is asking for verification",
        option_d="Nothing suspicious",
        correct_answer="B",
        explanation="This is domain spoofing! The real Amazon domain is 'amazon.com', not 'amaz0n.com'. Always carefully check the exact spelling of email domains.",
        category="Email Red Flags",
        difficulty="Medium"
    )
    
    # Link Safety
    db.add_quiz_question(
        question="Before clicking a link in an email, what should you do?",
        option_a="Click it quickly before it expires",
        option_b="Hover over it to see the actual URL destination",
        option_c="Forward it to a friend first",
        option_d="Nothing, links in emails are always safe",
        correct_answer="B",
        explanation="Always hover over links to see where they actually lead. The displayed text can say 'www.bank.com' but link to a malicious site.",
        category="Link Safety",
        difficulty="Easy"
    )
    
    db.add_quiz_question(
        question="Which URL is MOST LIKELY to be legitimate for PayPal?",
        option_a="http://paypal-secure.com",
        option_b="https://www.paypal.com",
        option_c="https://paypal.verify-account.com",
        option_d="http://www.paypal.support.net",
        correct_answer="B",
        explanation="The legitimate PayPal site is 'paypal.com' with HTTPS. Be wary of domains that add extra words before or after the company name.",
        category="Link Safety",
        difficulty="Medium"
    )
    
    db.add_quiz_question(
        question="What does 'HTTPS' in a URL indicate?",
        option_a="The website is definitely safe and legitimate",
        option_b="The connection is encrypted, but doesn't guarantee legitimacy",
        option_c="The website is hosted by Google",
        option_d="The website requires a password",
        correct_answer="B",
        explanation="HTTPS means the connection is encrypted, but phishing sites can also use HTTPS. Always verify the domain name is correct.",
        category="Link Safety",
        difficulty="Medium"
    )
    
    # Attachment Security
    db.add_quiz_question(
        question="You receive an unexpected email with a .exe file attachment from a colleague. What should you do?",
        option_a="Open it immediately since it's from a colleague",
        option_b="Contact your colleague through another method to verify they sent it",
        option_c="Forward it to your IT department",
        option_d="Delete the email without checking",
        correct_answer="B",
        explanation="Even if an email appears to be from a colleague, their account could be compromised. Always verify unexpected attachments through another communication channel.",
        category="Attachment Security",
        difficulty="Easy"
    )
    
    db.add_quiz_question(
        question="Which file extension is MOST DANGEROUS to open from an unknown sender?",
        option_a=".pdf",
        option_b=".txt",
        option_c=".exe",
        option_d=".jpg",
        correct_answer="C",
        explanation=".exe files are executable programs that can install malware on your computer. Never open .exe files from unknown or untrusted sources.",
        category="Attachment Security",
        difficulty="Easy"
    )
    
    # Social Engineering
    db.add_quiz_question(
        question="An email claims to be from your CEO requesting an urgent wire transfer. What should you do?",
        option_a="Process it immediately since it's from the CEO",
        option_b="Verify the request through a phone call or in-person conversation",
        option_c="Reply to the email asking for confirmation",
        option_d="Forward it to accounting",
        correct_answer="B",
        explanation="This is a common 'CEO fraud' attack. Always verify unusual requests through a separate communication channel, never by replying to the email.",
        category="Social Engineering",
        difficulty="Medium"
    )
    
    db.add_quiz_question(
        question="What is 'spear phishing'?",
        option_a="Phishing emails sent to everyone in a company",
        option_b="Targeted phishing attacks customized for specific individuals",
        option_c="Phishing through phone calls only",
        option_d="Phishing that uses fish-related themes",
        correct_answer="B",
        explanation="Spear phishing is highly targeted, using personal information about you to make the attack more convincing. These are harder to detect than generic phishing.",
        category="Social Engineering",
        difficulty="Hard"
    )
    
    # Best Practices
    db.add_quiz_question(
        question="What should you do if you accidentally clicked a suspicious link?",
        option_a="Do nothing and hope for the best",
        option_b="Immediately report it to IT/security team and change your passwords",
        option_c="Delete the email and forget about it",
        option_d="Turn off your computer",
        correct_answer="B",
        explanation="Quick action is crucial! Report the incident immediately so IT can take protective measures, and change your passwords from a secure device.",
        category="Best Practices",
        difficulty="Easy"
    )
    
    db.add_quiz_question(
        question="How often should you update your passwords for important accounts?",
        option_a="Never, if they're strong",
        option_b="Every 90 days or immediately if a breach is suspected",
        option_c="Once a year",
        option_d="Only when you forget them",
        correct_answer="B",
        explanation="Regular password updates (every 90 days) and immediate changes after suspected breaches help protect your accounts from compromised credentials.",
        category="Best Practices",
        difficulty="Medium"
    )
    
    print("Quiz questions seeded successfully!")


if __name__ == '__main__':
    # Initialize database and seed data on startup
    initialize()
    seed_quiz_questions()
    app.run(debug=True, host='0.0.0.0', port=5000)

