"""
Firebase Realtime Database module for Phishing Simulation System
Handles Firebase database operations for campaigns, users, messages, and events
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import json

# Try to import firebase-admin, if not available, we'll use a workaround
try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_AVAILABLE = True
except ImportError:
    print("⚠️  WARNING: firebase-admin not installed")
    print("   The app will use SQLite as a fallback")
    print("   To use Firebase, install: py -m ensurepip then py -m pip install firebase-admin")
    FIREBASE_AVAILABLE = False
    # Import the SQLite database as fallback
    from .database import Database as SQLiteDatabase

# Firebase credentials path
CRED_PATH = os.path.join(os.path.dirname(__file__), '..', 'firebase-credentials.json')
DATABASE_URL = 'https://phishing-simulation-proj-2e16c-default-rtdb.firebaseio.com/'


class FirebaseDatabase:
    """Firebase database manager for phishing simulation system"""
    
    def __init__(self, cred_path: str = CRED_PATH, database_url: str = DATABASE_URL):
        """Initialize Firebase connection"""
        self.cred_path = cred_path
        self.database_url = database_url
        self.init_firebase()
    
    def init_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
            print("Firebase already initialized")
        except ValueError:
            # Initialize Firebase
            cred = credentials.Certificate(self.cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': self.database_url
            })
            print(f"Firebase initialized with database: {self.database_url}")
    
    def get_ref(self, path: str):
        """Get database reference for a path"""
        return db.reference(path)
    
    def init_database(self):
        """Initialize database structure (compatibility method)"""
        print("Firebase Realtime Database ready")
    
    # User operations
    def add_user(self, email: str, name: str, department: Optional[str] = None) -> int:
        """Add a new user"""
        users_ref = self.get_ref('users')
        
        # Get next user ID
        all_users = users_ref.get() or {}
        user_id = max([int(k) for k in all_users.keys()], default=0) + 1 if all_users else 1
        
        user_data = {
            'id': user_id,
            'email': email,
            'name': name,
            'department': department,
            'created_at': datetime.now().isoformat()
        }
        
        users_ref.child(str(user_id)).set(user_data)
        
        # Initialize risk record
        risk_ref = self.get_ref('user_risk')
        risk_ref.child(str(user_id)).set({
            'user_id': user_id,
            'risk_score': 0,
            'risk_category': 'Low',
            'is_repeat_offender': False,
            'last_updated': datetime.now().isoformat()
        })
        
        return user_id
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        users_ref = self.get_ref('users')
        users_data = users_ref.get() or {}
        return [v for v in users_data.values()] if users_data else []
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        user_ref = self.get_ref(f'users/{user_id}')
        return user_ref.get()
    
    # Campaign operations
    def create_campaign(self, name: str, difficulty: str, template_id: int,
                       start_date: Optional[str] = None, target_segment: str = 'all') -> int:
        """Create a new campaign"""
        campaigns_ref = self.get_ref('campaigns')
        
        # Get next campaign ID
        all_campaigns = campaigns_ref.get() or {}
        campaign_id = max([int(k) for k in all_campaigns.keys()], default=0) + 1 if all_campaigns else 1
        
        campaign_data = {
            'id': campaign_id,
            'name': name,
            'difficulty': difficulty,
            'template_id': template_id,
            'status': 'scheduled',
            'start_date': start_date,
            'target_segment': target_segment,
            'created_at': datetime.now().isoformat(),
            'launched_at': None,
            'completed_at': None,
            'end_date': None
        }
        
        campaigns_ref.child(str(campaign_id)).set(campaign_data)
        
        # Initialize metrics
        metrics_ref = self.get_ref('campaign_metrics')
        metrics_ref.child(str(campaign_id)).set({
            'campaign_id': campaign_id,
            'total_sent': 0,
            'total_clicks': 0,
            'total_reports': 0,
            'total_ignores': 0,
            'training_started': 0,
            'training_completed': 0,
            'training_failed': 0,
            'click_rate': 0.0,
            'report_rate': 0.0,
            'training_completion_rate': 0.0,
            'last_updated': datetime.now().isoformat()
        })
        
        return campaign_id
    
    def get_campaign(self, campaign_id: int) -> Optional[Dict]:
        """Get campaign by ID"""
        campaign_ref = self.get_ref(f'campaigns/{campaign_id}')
        return campaign_ref.get()
    
    def get_all_campaigns(self) -> List[Dict]:
        """Get all campaigns"""
        campaigns_ref = self.get_ref('campaigns')
        campaigns_data = campaigns_ref.get() or {}
        campaigns = [v for v in campaigns_data.values()] if campaigns_data else []
        # Sort by created_at descending
        campaigns.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return campaigns
    
    def update_campaign_status(self, campaign_id: int, status: str):
        """Update campaign status"""
        campaign_ref = self.get_ref(f'campaigns/{campaign_id}')
        
        update_data = {'status': status}
        
        if status == 'active':
            update_data['launched_at'] = datetime.now().isoformat()
        elif status == 'completed':
            update_data['completed_at'] = datetime.now().isoformat()
        
        campaign_ref.update(update_data)
    
    # Message operations
    def create_message(self, campaign_id: int, user_id: int) -> int:
        """Create a message record"""
        messages_ref = self.get_ref('messages')
        
        # Get next message ID
        all_messages = messages_ref.get() or {}
        message_id = max([int(k) for k in all_messages.keys()], default=0) + 1 if all_messages else 1
        
        message_data = {
            'id': message_id,
            'campaign_id': campaign_id,
            'user_id': user_id,
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        messages_ref.child(str(message_id)).set(message_data)
        return message_id
    
    def get_messages_by_campaign(self, campaign_id: int) -> List[Dict]:
        """Get all messages for a campaign"""
        messages_ref = self.get_ref('messages')
        all_messages = messages_ref.get() or {}
        
        campaign_messages = [
            v for v in all_messages.values() 
            if v.get('campaign_id') == campaign_id
        ] if all_messages else []
        
        return campaign_messages
    
    # Event operations
    def log_event(self, message_id: int, user_id: int, campaign_id: int,
                  event_type: str, metadata: Optional[str] = None) -> int:
        """Log a user event"""
        events_ref = self.get_ref('events')
        
        # Get next event ID
        all_events = events_ref.get() or {}
        event_id = max([int(k) for k in all_events.keys()], default=0) + 1 if all_events else 1
        
        event_data = {
            'id': event_id,
            'message_id': message_id,
            'user_id': user_id,
            'campaign_id': campaign_id,
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata
        }
        
        events_ref.child(str(event_id)).set(event_data)
        
        # Update metrics
        self.update_campaign_metrics(campaign_id)
        
        return event_id
    
    def get_user_events(self, user_id: int) -> List[Dict]:
        """Get all events for a user"""
        events_ref = self.get_ref('events')
        all_events = events_ref.get() or {}
        
        user_events = [
            v for v in all_events.values() 
            if v.get('user_id') == user_id
        ] if all_events else []
        
        # Sort by timestamp descending
        user_events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return user_events
    
    def get_campaign_events(self, campaign_id: int) -> List[Dict]:
        """Get all events for a campaign"""
        events_ref = self.get_ref('events')
        all_events = events_ref.get() or {}
        
        campaign_events = [
            v for v in all_events.values() 
            if v.get('campaign_id') == campaign_id
        ] if all_events else []
        
        # Sort by timestamp descending
        campaign_events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return campaign_events
    
    # Risk operations
    def update_user_risk(self, user_id: int):
        """Calculate and update user risk score"""
        events = self.get_user_events(user_id)
        
        score = 0
        click_count = 0
        
        for event in events:
            if event['event_type'] == 'click':
                score += 3
                click_count += 1
            elif event['event_type'] == 'report':
                score -= 2
            elif event['event_type'] == 'training_failed':
                score += 2
        
        # Determine category
        if score <= 2:
            category = 'Low'
        elif score <= 6:
            category = 'Medium'
        else:
            category = 'High'
        
        # Check repeat offender status
        is_repeat_offender = click_count >= 2
        
        risk_ref = self.get_ref(f'user_risk/{user_id}')
        risk_ref.update({
            'risk_score': score,
            'risk_category': category,
            'is_repeat_offender': is_repeat_offender,
            'last_updated': datetime.now().isoformat()
        })
    
    def get_user_risk(self, user_id: int) -> Optional[Dict]:
        """Get user risk information"""
        risk_ref = self.get_ref(f'user_risk/{user_id}')
        return risk_ref.get()
    
    def get_users_by_risk_category(self, category: str) -> List[Dict]:
        """Get all users in a risk category"""
        users_ref = self.get_ref('users')
        risk_ref = self.get_ref('user_risk')
        
        all_users = users_ref.get() or {}
        all_risks = risk_ref.get() or {}
        
        result = []
        for user_id, user_data in all_users.items():
            risk_data = all_risks.get(user_id, {})
            if risk_data.get('risk_category') == category:
                # Merge user and risk data
                merged = {**user_data, **risk_data}
                result.append(merged)
        
        return result
    
    # Template operations
    def add_template(self, name: str, difficulty: str, subject: str,
                    sender_name: str, sender_email: str, body_content: str,
                    link_text: str) -> int:
        """Add a phishing template"""
        templates_ref = self.get_ref('templates')
        
        # Get next template ID
        all_templates = templates_ref.get() or {}
        template_id = max([int(k) for k in all_templates.keys()], default=0) + 1 if all_templates else 1
        
        template_data = {
            'id': template_id,
            'name': name,
            'difficulty': difficulty,
            'subject': subject,
            'sender_name': sender_name,
            'sender_email': sender_email,
            'body_content': body_content,
            'link_text': link_text,
            'created_at': datetime.now().isoformat()
        }
        
        templates_ref.child(str(template_id)).set(template_data)
        return template_id
    
    def get_template(self, template_id: int) -> Optional[Dict]:
        """Get template by ID"""
        template_ref = self.get_ref(f'templates/{template_id}')
        return template_ref.get()
    
    def get_all_templates(self) -> List[Dict]:
        """Get all templates"""
        templates_ref = self.get_ref('templates')
        templates_data = templates_ref.get() or {}
        templates = [v for v in templates_data.values()] if templates_data else []
        # Sort by difficulty and created_at
        templates.sort(key=lambda x: (x.get('difficulty', ''), x.get('created_at', '')))
        return templates
    
    # Metrics operations
    def update_campaign_metrics(self, campaign_id: int):
        """Update campaign metrics based on events"""
        events = self.get_campaign_events(campaign_id)
        messages = self.get_messages_by_campaign(campaign_id)
        
        total_sent = len(messages)
        total_clicks = sum(1 for e in events if e['event_type'] == 'click')
        total_reports = sum(1 for e in events if e['event_type'] == 'report')
        total_ignores = sum(1 for e in events if e['event_type'] == 'ignore')
        training_started = sum(1 for e in events if e['event_type'] == 'training_started')
        training_completed = sum(1 for e in events if e['event_type'] == 'training_completed')
        training_failed = sum(1 for e in events if e['event_type'] == 'training_failed')
        
        click_rate = (total_clicks / total_sent * 100) if total_sent > 0 else 0
        report_rate = (total_reports / total_sent * 100) if total_sent > 0 else 0
        training_completion_rate = (training_completed / training_started * 100) if training_started > 0 else 0
        
        metrics_ref = self.get_ref(f'campaign_metrics/{campaign_id}')
        metrics_ref.update({
            'total_sent': total_sent,
            'total_clicks': total_clicks,
            'total_reports': total_reports,
            'total_ignores': total_ignores,
            'training_started': training_started,
            'training_completed': training_completed,
            'training_failed': training_failed,
            'click_rate': round(click_rate, 2),
            'report_rate': round(report_rate, 2),
            'training_completion_rate': round(training_completion_rate, 2),
            'last_updated': datetime.now().isoformat()
        })
    
    def get_campaign_metrics(self, campaign_id: int) -> Optional[Dict]:
        """Get metrics for a campaign"""
        metrics_ref = self.get_ref(f'campaign_metrics/{campaign_id}')
        return metrics_ref.get()
    
    def get_all_metrics(self) -> List[Dict]:
        """Get metrics for all campaigns"""
        metrics_ref = self.get_ref('campaign_metrics')
        campaigns_ref = self.get_ref('campaigns')
        
        all_metrics = metrics_ref.get() or {}
        all_campaigns = campaigns_ref.get() or {}
        
        result = []
        for campaign_id, metrics_data in all_metrics.items():
            campaign_data = all_campaigns.get(campaign_id, {})
            merged = {
                **metrics_data,
                'name': campaign_data.get('name'),
                'difficulty': campaign_data.get('difficulty'),
                'status': campaign_data.get('status'),
                'start_date': campaign_data.get('start_date')
            }
            result.append(merged)
        
        # Sort by start_date descending
        result.sort(key=lambda x: x.get('start_date', '') or '', reverse=True)
        return result
    
    # Quiz operations
    def add_quiz_question(self, question: str, option_a: str, option_b: str, option_c: str, 
                          option_d: str, correct_answer: str, explanation: str, 
                          category: str, difficulty: str = 'Medium') -> int:
        """Add a new quiz question"""
        questions_ref = self.get_ref('quiz_questions')
        
        # Get next question ID
        all_questions = questions_ref.get() or {}
        question_id = max([int(k) for k in all_questions.keys()], default=0) + 1 if all_questions else 1
        
        question_data = {
            'id': question_id,
            'question': question,
            'option_a': option_a,
            'option_b': option_b,
            'option_c': option_c,
            'option_d': option_d,
            'correct_answer': correct_answer,
            'explanation': explanation,
            'category': category,
            'difficulty': difficulty,
            'created_at': datetime.now().isoformat()
        }
        
        questions_ref.child(str(question_id)).set(question_data)
        return question_id
    
    def get_quiz_questions(self, limit: int = None) -> List[Dict]:
        """Get all quiz questions (without revealing correct answers)"""
        questions_ref = self.get_ref('quiz_questions')
        all_questions = questions_ref.get() or {}
        
        questions = []
        for q_id, q_data in all_questions.items():
            questions.append({
                'id': q_data['id'],
                'question': q_data['question'],
                'options': {
                    'A': q_data['option_a'],
                    'B': q_data['option_b'],
                    'C': q_data['option_c'],
                    'D': q_data['option_d']
                },
                'category': q_data['category'],
                'difficulty': q_data['difficulty']
            })
            if limit and len(questions) >= limit:
                break
        return questions
    
    def submit_quiz_answer(self, user_id: int, question_id: int, selected_answer: str) -> Dict:
        """Submit a quiz answer and return whether it's correct with explanation"""
        question_ref = self.get_ref(f'quiz_questions/{question_id}')
        question_data = question_ref.get()
        
        if not question_data:
            return {'error': 'Question not found'}
        
        correct_answer = question_data['correct_answer']
        explanation = question_data['explanation']
        is_correct = (selected_answer == correct_answer)
        
        # Record the attempt
        attempts_ref = self.get_ref('quiz_attempts')
        all_attempts = attempts_ref.get() or {}
        attempt_id = max([int(k) for k in all_attempts.keys()], default=0) + 1 if all_attempts else 1
        
        attempts_ref.child(str(attempt_id)).set({
            'user_id': user_id,
            'question_id': question_id,
            'selected_answer': selected_answer,
            'is_correct': is_correct,
            'attempted_at': datetime.now().isoformat()
        })
        
        return {
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'explanation': explanation
        }
    
    def get_user_quiz_stats(self, user_id: int) -> Dict:
        """Get quiz statistics for a user"""
        attempts_ref = self.get_ref('quiz_attempts')
        all_attempts = attempts_ref.get() or {}
        
        user_attempts = [v for v in all_attempts.values() if v.get('user_id') == user_id]
        
        total_attempts = len(user_attempts)
        correct_answers = sum(1 for a in user_attempts if a.get('is_correct'))
        questions_attempted = len(set(a.get('question_id') for a in user_attempts))
        
        accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'total_attempts': total_attempts,
            'correct_answers': correct_answers,
            'questions_attempted': questions_attempted,
            'accuracy': round(accuracy, 1)
        }

    def get_connection(self):

        """Compatibility method - not needed for Firebase"""
        return None


# Convenience function
def get_database():
    """Get database instance - Firebase if available, SQLite otherwise"""
    if FIREBASE_AVAILABLE:
        return FirebaseDatabase()
    else:
        print("📊 Using SQLite database (Firebase not available)")
        return SQLiteDatabase()


if __name__ == '__main__':
    # Initialize database when run directly
    if FIREBASE_AVAILABLE:
        db = FirebaseDatabase()
        print("Firebase database setup complete!")
    else:
        db = SQLiteDatabase()
        print("SQLite database setup complete (Firebase fallback)")

