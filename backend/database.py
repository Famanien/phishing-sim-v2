"""
Database module for Phishing Simulation System
Handles SQLite database operations for campaigns, users, messages, and events
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'phishing_sim.db')


class Database:
    """Database manager for phishing simulation system"""
    
    def __init__(self, db_path: str = DB_PATH):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create campaigns table with automation fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                difficulty TEXT CHECK(difficulty IN ('Easy', 'Medium', 'Hard')) DEFAULT 'Easy',
                template_id INTEGER,
                status TEXT CHECK(status IN ('scheduled', 'active', 'completed', 'paused')) DEFAULT 'scheduled',
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                target_segment TEXT CHECK(target_segment IN ('all', 'high_risk', 'medium_risk', 'low_risk')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                launched_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        # Create messages table (tracks individual phishing emails sent)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT CHECK(status IN ('sent', 'delivered', 'bounced')) DEFAULT 'sent',
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create events table (tracks user actions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                campaign_id INTEGER NOT NULL,
                event_type TEXT CHECK(event_type IN ('click', 'report', 'ignore', 'training_started', 'training_completed', 'training_failed')) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (message_id) REFERENCES messages(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')
        
        # Create user_risk table (tracks risk scores and categories)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_risk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                risk_score INTEGER DEFAULT 0,
                risk_category TEXT CHECK(risk_category IN ('Low', 'Medium', 'High')) DEFAULT 'Low',
                is_repeat_offender BOOLEAN DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                difficulty TEXT CHECK(difficulty IN ('Easy', 'Medium', 'Hard')) DEFAULT 'Easy',
                subject TEXT NOT NULL,
                sender_name TEXT NOT NULL,
                sender_email TEXT NOT NULL,
                body_content TEXT NOT NULL,
                link_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create campaign_metrics table (for tracking performance)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER UNIQUE NOT NULL,
                total_sent INTEGER DEFAULT 0,
                total_clicks INTEGER DEFAULT 0,
                total_reports INTEGER DEFAULT 0,
                total_ignores INTEGER DEFAULT 0,
                training_started INTEGER DEFAULT 0,
                training_completed INTEGER DEFAULT 0,
                training_failed INTEGER DEFAULT 0,
                click_rate REAL DEFAULT 0.0,
                report_rate REAL DEFAULT 0.0,
                training_completion_rate REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')
        
        # Create quiz_questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT CHECK(correct_answer IN ('A', 'B', 'C', 'D')) NOT NULL,
                explanation TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT CHECK(difficulty IN ('Easy', 'Medium', 'Hard')) DEFAULT 'Medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create quiz_attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                selected_answer TEXT CHECK(selected_answer IN ('A', 'B', 'C', 'D')) NOT NULL,
                is_correct BOOLEAN NOT NULL,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (question_id) REFERENCES quiz_questions(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
    
    # User operations
    def add_user(self, email: str, name: str, department: str = None) -> int:
        """Add a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (email, name, department) VALUES (?, ?, ?)',
            (email, name, department)
        )
        user_id = cursor.lastrowid
        
        # Initialize risk record
        cursor.execute(
            'INSERT INTO user_risk (user_id) VALUES (?)',
            (user_id,)
        )
        
        conn.commit()
        conn.close()
        return user_id
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # Campaign operations
    def create_campaign(self, name: str, difficulty: str, template_id: int,
                       start_date: str = None, target_segment: str = 'all') -> int:
        """Create a new campaign"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO campaigns (name, difficulty, template_id, start_date, target_segment)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, difficulty, template_id, start_date, target_segment))
        campaign_id = cursor.lastrowid
        
        # Initialize metrics
        cursor.execute(
            'INSERT INTO campaign_metrics (campaign_id) VALUES (?)',
            (campaign_id,)
        )
        
        conn.commit()
        conn.close()
        return campaign_id
    
    def get_campaign(self, campaign_id: int) -> Optional[Dict]:
        """Get campaign by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_campaigns(self) -> List[Dict]:
        """Get all campaigns"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM campaigns ORDER BY created_at DESC')
        campaigns = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return campaigns
    
    def update_campaign_status(self, campaign_id: int, status: str):
        """Update campaign status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        timestamp_field = None
        if status == 'active':
            timestamp_field = 'launched_at'
        elif status == 'completed':
            timestamp_field = 'completed_at'
        
        if timestamp_field:
            cursor.execute(f'''
                UPDATE campaigns 
                SET status = ?, {timestamp_field} = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, campaign_id))
        else:
            cursor.execute(
                'UPDATE campaigns SET status = ? WHERE id = ?',
                (status, campaign_id)
            )
        
        conn.commit()
        conn.close()
    
    # Message operations
    def create_message(self, campaign_id: int, user_id: int) -> int:
        """Create a message record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO messages (campaign_id, user_id) VALUES (?, ?)',
            (campaign_id, user_id)
        )
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id
    
    def get_messages_by_campaign(self, campaign_id: int) -> List[Dict]:
        """Get all messages for a campaign"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM messages WHERE campaign_id = ?',
            (campaign_id,)
        )
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages
    
    # Event operations
    def log_event(self, message_id: int, user_id: int, campaign_id: int,
                  event_type: str, metadata: str = None) -> int:
        """Log a user event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (message_id, user_id, campaign_id, event_type, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (message_id, user_id, campaign_id, event_type, metadata))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Update metrics
        self.update_campaign_metrics(campaign_id)
        
        return event_id
    
    def get_user_events(self, user_id: int) -> List[Dict]:
        """Get all events for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM events WHERE user_id = ? ORDER BY timestamp DESC',
            (user_id,)
        )
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return events
    
    def get_campaign_events(self, campaign_id: int) -> List[Dict]:
        """Get all events for a campaign"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM events WHERE campaign_id = ? ORDER BY timestamp DESC',
            (campaign_id,)
        )
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return events
    
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
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE user_risk 
            SET risk_score = ?, risk_category = ?, is_repeat_offender = ?, last_updated = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (score, category, is_repeat_offender, user_id))
        conn.commit()
        conn.close()
    
    def get_user_risk(self, user_id: int) -> Optional[Dict]:
        """Get user risk information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_risk WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_users_by_risk_category(self, category: str) -> List[Dict]:
        """Get all users in a risk category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, ur.risk_score, ur.risk_category, ur.is_repeat_offender
            FROM users u
            JOIN user_risk ur ON u.id = ur.user_id
            WHERE ur.risk_category = ?
        ''', (category,))
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    
    # Template operations
    def add_template(self, name: str, difficulty: str, subject: str,
                    sender_name: str, sender_email: str, body_content: str,
                    link_text: str) -> int:
        """Add a phishing template"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO templates (name, difficulty, subject, sender_name, sender_email, body_content, link_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, difficulty, subject, sender_name, sender_email, body_content, link_text))
        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return template_id
    
    def get_template(self, template_id: int) -> Optional[Dict]:
        """Get template by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_templates(self) -> List[Dict]:
        """Get all templates"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM templates ORDER BY difficulty, created_at')
        templates = [dict(row) for row in cursor.fetchall()]
        conn.close()
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
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE campaign_metrics
            SET total_sent = ?, total_clicks = ?, total_reports = ?, total_ignores = ?,
                training_started = ?, training_completed = ?, training_failed = ?,
                click_rate = ?, report_rate = ?, training_completion_rate = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE campaign_id = ?
        ''', (total_sent, total_clicks, total_reports, total_ignores,
              training_started, training_completed, training_failed,
              click_rate, report_rate, training_completion_rate, campaign_id))
        conn.commit()
        conn.close()
    
    def get_campaign_metrics(self, campaign_id: int) -> Optional[Dict]:
        """Get metrics for a campaign"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM campaign_metrics WHERE campaign_id = ?', (campaign_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_all_metrics(self) -> List[Dict]:
        """Get metrics for all campaigns"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cm.*, c.name, c.difficulty, c.status, c.start_date
            FROM campaign_metrics cm
            JOIN campaigns c ON cm.campaign_id = c.id
            ORDER BY c.start_date DESC
        ''')
        metrics = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return metrics
    
    # Quiz operations
    def add_quiz_question(self, question: str, option_a: str, option_b: str, option_c: str, 
                          option_d: str, correct_answer: str, explanation: str, 
                          category: str, difficulty: str = 'Medium') -> int:
        """Add a new quiz question"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO quiz_questions 
            (question, option_a, option_b, option_c, option_d, correct_answer, explanation, category, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (question, option_a, option_b, option_c, option_d, correct_answer, explanation, category, difficulty))
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return question_id
    
    def get_quiz_questions(self, limit: int = None) -> List[Dict]:
        """Get all quiz questions (without revealing correct answers)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT id, question, option_a, option_b, option_c, option_d, category, difficulty FROM quiz_questions'
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        questions = []
        for row in rows:
            questions.append({
                'id': row['id'],
                'question': row['question'],
                'options': {
                    'A': row['option_a'],
                    'B': row['option_b'],
                    'C': row['option_c'],
                    'D': row['option_d']
                },
                'category': row['category'],
                'difficulty': row['difficulty']
            })
        return questions
    
    def submit_quiz_answer(self, user_id: int, question_id: int, selected_answer: str) -> Dict:
        """Submit a quiz answer and return whether it's correct with explanation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get the correct answer and explanation
        cursor.execute('''
            SELECT correct_answer, explanation FROM quiz_questions WHERE id = ?
        ''', (question_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {'error': 'Question not found'}
        
        correct_answer = row['correct_answer']
        explanation = row['explanation']
        is_correct = (selected_answer == correct_answer)
        
        # Record the attempt
        cursor.execute('''
            INSERT INTO quiz_attempts (user_id, question_id, selected_answer, is_correct)
            VALUES (?, ?, ?, ?)
        ''', (user_id, question_id, selected_answer, is_correct))
        
        conn.commit()
        conn.close()
        
        return {
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'explanation': explanation
        }
    
    def get_user_quiz_stats(self, user_id: int) -> Dict:
        """Get quiz statistics for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
                COUNT(DISTINCT question_id) as questions_attempted
            FROM quiz_attempts
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        total_attempts = row['total_attempts'] or 0
        correct_answers = row['correct_answers'] or 0
        questions_attempted = row['questions_attempted'] or 0
        
        accuracy = (correct_answers / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'total_attempts': total_attempts,
            'correct_answers': correct_answers,
            'questions_attempted': questions_attempted,
            'accuracy': round(accuracy, 1)
        }


    # -------------------------------------------------------------------------
    # Sprint 6 – Behaviour Analytics
    # -------------------------------------------------------------------------

    def get_repeat_offenders(self) -> List[Dict]:
        """
        Return users who clicked phishing links 2+ times across all campaigns,
        or who clicked after completing training (repeat offender rules).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                u.id            AS user_id,
                u.name,
                u.email,
                u.department,
                COUNT(e.id)     AS total_clicks,
                COUNT(DISTINCT e.campaign_id) AS campaigns_clicked,
                ur.risk_score,
                ur.risk_category,
                ur.is_repeat_offender
            FROM events e
            JOIN users u  ON e.user_id    = u.id
            LEFT JOIN user_risk ur ON ur.user_id = u.id
            WHERE e.event_type = 'click'
            GROUP BY e.user_id
            HAVING COUNT(e.id) >= 2
            ORDER BY total_clicks DESC
        ''')
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        # Also flag users who clicked AFTER completing training
        conn2 = self.get_connection()
        cursor2 = conn2.cursor()
        cursor2.execute('''
            SELECT DISTINCT e_click.user_id
            FROM events e_click
            JOIN events e_train
                ON  e_click.user_id    = e_train.user_id
                AND e_train.event_type = 'training_completed'
                AND e_click.event_type = 'click'
                AND e_click.timestamp  > e_train.timestamp
        ''')
        post_training_ids = {r[0] for r in cursor2.fetchall()}
        conn2.close()

        for row in rows:
            row['clicked_after_training'] = row['user_id'] in post_training_ids

        # Include users who clicked after training but only once
        if post_training_ids:
            existing_ids = {r['user_id'] for r in rows}
            conn3 = self.get_connection()
            cursor3 = conn3.cursor()
            for uid in post_training_ids - existing_ids:
                cursor3.execute('''
                    SELECT u.id AS user_id, u.name, u.email, u.department,
                           COUNT(e.id) AS total_clicks,
                           COUNT(DISTINCT e.campaign_id) AS campaigns_clicked,
                           ur.risk_score, ur.risk_category, ur.is_repeat_offender
                    FROM events e
                    JOIN users u      ON e.user_id     = u.id
                    LEFT JOIN user_risk ur ON ur.user_id = u.id
                    WHERE e.event_type = 'click' AND e.user_id = ?
                    GROUP BY e.user_id
                ''', (uid,))
                extra = cursor3.fetchone()
                if extra:
                    d = dict(extra)
                    d['clicked_after_training'] = True
                    rows.append(d)
            conn3.close()

        return rows

    def get_behaviour_trend_report(self) -> List[Dict]:
        """
        Return per-campaign behaviour KPIs sorted chronologically.
        Each row: campaign name, difficulty, click_rate, report_rate,
        training_completion_rate.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                c.id,
                c.name              AS campaign,
                c.difficulty,
                c.start_date,
                cm.total_sent,
                ROUND(cm.click_rate,            1) AS click_rate,
                ROUND(cm.report_rate,           1) AS report_rate,
                ROUND(cm.training_completion_rate, 1) AS training_completion_rate,
                cm.total_clicks,
                cm.total_reports,
                cm.training_completed
            FROM campaign_metrics cm
            JOIN campaigns c ON c.id = cm.campaign_id
            ORDER BY c.start_date ASC, c.id ASC
        ''')
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_pattern_insights(self) -> Dict:
        """
        Returns:
          - top_templates: templates ranked by click_rate
          - department_risk:  avg click rate per department
          - repeat_offender_count: total repeat offenders
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Top templates by click rate
        cursor.execute('''
            SELECT
                t.name          AS template_name,
                t.difficulty,
                COUNT(e.id)     AS total_clicks,
                COUNT(m.id)     AS total_sent,
                CASE WHEN COUNT(m.id) > 0
                     THEN ROUND(COUNT(e.id) * 100.0 / COUNT(m.id), 1)
                     ELSE 0 END AS click_rate
            FROM templates t
            LEFT JOIN campaigns c   ON c.template_id = t.id
            LEFT JOIN messages  m   ON m.campaign_id = c.id
            LEFT JOIN events    e   ON e.message_id  = m.id
                                   AND e.event_type  = 'click'
            GROUP BY t.id
            ORDER BY click_rate DESC
            LIMIT 5
        ''')
        top_templates = [dict(r) for r in cursor.fetchall()]

        # Department vulnerability
        cursor.execute('''
            SELECT
                u.department,
                COUNT(e.id)     AS total_clicks,
                COUNT(m.id)     AS total_sent,
                CASE WHEN COUNT(m.id) > 0
                     THEN ROUND(COUNT(e.id) * 100.0 / COUNT(m.id), 1)
                     ELSE 0 END AS click_rate
            FROM users u
            LEFT JOIN messages m ON m.user_id    = u.id
            LEFT JOIN events   e ON e.message_id = m.id
                                AND e.event_type = 'click'
            WHERE u.department IS NOT NULL
            GROUP BY u.department
            ORDER BY click_rate DESC
        ''')
        department_risk = [dict(r) for r in cursor.fetchall()]

        # Repeat offender count
        cursor.execute('SELECT COUNT(*) FROM user_risk WHERE is_repeat_offender = 1')
        repeat_count = cursor.fetchone()[0]

        conn.close()
        return {
            'top_templates': top_templates,
            'department_risk': department_risk,
            'repeat_offender_count': repeat_count
        }

    def get_kpi_summary(self) -> Dict:
        """
        Return overall KPI metrics across all completed/active campaigns.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                SUM(cm.total_sent)            AS total_sent,
                SUM(cm.total_clicks)          AS total_clicks,
                SUM(cm.total_reports)         AS total_reports,
                SUM(cm.training_completed)    AS training_completed,
                SUM(cm.training_started)      AS training_started,
                CASE WHEN SUM(cm.total_sent) > 0
                     THEN ROUND(SUM(cm.total_clicks)  * 100.0 / SUM(cm.total_sent), 1)
                     ELSE 0 END AS overall_click_rate,
                CASE WHEN SUM(cm.total_sent) > 0
                     THEN ROUND(SUM(cm.total_reports) * 100.0 / SUM(cm.total_sent), 1)
                     ELSE 0 END AS overall_report_rate,
                CASE WHEN SUM(cm.training_started) > 0
                     THEN ROUND(SUM(cm.training_completed) * 100.0 / SUM(cm.training_started), 1)
                     ELSE 0 END AS overall_training_completion
            FROM campaign_metrics cm
        ''')
        row = dict(cursor.fetchone())

        cursor.execute('SELECT COUNT(*) FROM user_risk WHERE is_repeat_offender = 1')
        row['repeat_offender_count'] = cursor.fetchone()[0]

        conn.close()
        return row

    def export_repeat_offenders_csv(self) -> str:
        """Return a CSV string of repeat offenders for download."""
        offenders = self.get_repeat_offenders()
        lines = ['Name,Email,Department,Total Clicks,Campaigns Clicked,Risk Category,Clicked After Training']
        for o in offenders:
            lines.append(
                f"{o['name']},{o['email']},{o.get('department','')},"
                f"{o['total_clicks']},{o['campaigns_clicked']},"
                f"{o.get('risk_category','')},{o.get('clicked_after_training',False)}"
            )
        return '\n'.join(lines)

    def get_risk_distribution(self) -> Dict:
        """Return count of users in each risk tier and total messages for overview."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Risk tier counts
        cursor.execute('''
            SELECT
                SUM(CASE WHEN risk_category = 'High'   THEN 1 ELSE 0 END) AS high_count,
                SUM(CASE WHEN risk_category = 'Medium' THEN 1 ELSE 0 END) AS medium_count,
                SUM(CASE WHEN risk_category = 'Low'    THEN 1 ELSE 0 END) AS low_count,
                COUNT(*) AS total_users
            FROM user_risk
        ''')
        risk = dict(cursor.fetchone())

        # Users with no risk record yet
        cursor.execute('''
            SELECT COUNT(*) FROM users u
            LEFT JOIN user_risk ur ON ur.user_id = u.id
            WHERE ur.user_id IS NULL
        ''')
        risk['unassessed'] = cursor.fetchone()[0]

        # Total users across the system
        cursor.execute('SELECT COUNT(*) FROM users')
        risk['all_users'] = cursor.fetchone()[0]

        conn.close()
        return risk

    def get_campaign_improvement(self) -> Dict:
        """Compare first vs latest campaign KPIs to show improvement over time."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                c.name AS campaign,
                c.start_date,
                ROUND(cm.click_rate, 1)             AS click_rate,
                ROUND(cm.report_rate, 1)            AS report_rate,
                ROUND(cm.training_completion_rate, 1) AS training_completion_rate,
                cm.total_sent
            FROM campaign_metrics cm
            JOIN campaigns c ON c.id = cm.campaign_id
            ORDER BY c.start_date ASC, c.id ASC
        ''')
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if not rows:
            return {'has_data': False}

        first = rows[0]
        latest = rows[-1]

        return {
            'has_data': True,
            'campaign_count': len(rows),
            'first': first,
            'latest': latest,
            'click_delta':    round((latest['click_rate']   or 0) - (first['click_rate']   or 0), 1),
            'report_delta':   round((latest['report_rate']  or 0) - (first['report_rate']  or 0), 1),
            'training_delta': round((latest['training_completion_rate'] or 0) - (first['training_completion_rate'] or 0), 1),
        }



    def get_metrics_by_risk_group(self) -> List:
        """Return avg click/report/training metrics broken down by risk category (High/Medium/Low)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Build per-user aggregates from messages + events, then group by risk tier
        cursor.execute('''
            SELECT
                ur.risk_category,
                COUNT(DISTINCT ur.user_id) AS user_count,
                ROUND(
                    100.0 * SUM(CASE WHEN e_click.id IS NOT NULL THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(DISTINCT m.id), 0), 1
                ) AS avg_click_rate,
                ROUND(
                    100.0 * SUM(CASE WHEN e_rep.id IS NOT NULL THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(DISTINCT m.id), 0), 1
                ) AS avg_report_rate,
                ROUND(
                    100.0 * SUM(CASE WHEN e_train.id IS NOT NULL THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(DISTINCT m.id), 0), 1
                ) AS avg_training_rate
            FROM user_risk ur
            LEFT JOIN messages m
                ON m.user_id = ur.user_id
            LEFT JOIN events e_click
                ON e_click.message_id = m.id AND e_click.event_type = 'click'
            LEFT JOIN events e_rep
                ON e_rep.message_id = m.id AND e_rep.event_type = 'report'
            LEFT JOIN events e_train
                ON e_train.message_id = m.id AND e_train.event_type = 'training_completed'
            WHERE ur.risk_category IN ('High', 'Medium', 'Low')
            GROUP BY ur.risk_category
            ORDER BY CASE ur.risk_category
                WHEN 'High'   THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low'    THEN 3
            END
        ''')
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows


# Convenience function
def get_database() -> Database:
    """Get database instance"""
    return Database()


if __name__ == '__main__':
    # Initialize database when run directly
    db = Database()
    print("Database setup complete!")
