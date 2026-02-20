"""
Campaign Automation Module
Handles automated campaign launching, scheduling, and user segmentation
"""

from .database import Database
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class CampaignAutomation:
    """Manages automated campaign operations"""
    
    def __init__(self):
        self.db = Database()
    
    def launch_campaign(self, campaign_id: int) -> Dict:
        """
        Auto-launch a campaign: select target users, create messages, activate campaign
        
        Returns:
            Dict with launch results including number of messages sent
        """
        campaign = self.db.get_campaign(campaign_id)
        if not campaign:
            return {'success': False, 'error': 'Campaign not found'}
        
        if campaign['status'] != 'scheduled':
            return {'success': False, 'error': f'Campaign status is {campaign["status"]}, must be scheduled'}
        
        # Select target users based on segmentation
        target_users = self._select_target_users(campaign['target_segment'])
        
        if not target_users:
            return {'success': False, 'error': 'No target users found'}
        
        # Create message records for each user
        message_ids = []
        for user in target_users:
            message_id = self.db.create_message(campaign_id, user['id'])
            message_ids.append(message_id)
        
        # Update campaign status to active
        self.db.update_campaign_status(campaign_id, 'active')
        
        # Update metrics
        self.db.update_campaign_metrics(campaign_id)
        
        return {
            'success': True,
            'campaign_id': campaign_id,
            'campaign_name': campaign['name'],
            'messages_sent': len(message_ids),
            'target_users': len(target_users),
            'launched_at': datetime.now().isoformat()
        }
    
    def _select_target_users(self, target_segment: str) -> List[Dict]:
        """
        Select users based on segmentation rules
        
        Args:
            target_segment: 'all', 'high_risk', 'medium_risk', or 'low_risk'
        
        Returns:
            List of user dictionaries
        """
        if target_segment == 'all':
            return self.db.get_all_users()
        elif target_segment in ['high_risk', 'medium_risk', 'low_risk']:
            # Convert to proper case for database query
            category = target_segment.replace('_', ' ').title()
            return self.db.get_users_by_risk_category(category)
        else:
            return []
    
    def schedule_weekly_campaign(self, template_id: int, difficulty: str,
                                 target_segment: str = 'all', week_number: int = 5) -> int:
        """
        Schedule a weekly campaign
        
        Args:
            template_id: Template to use
            difficulty: Campaign difficulty level
            target_segment: Target user segment
            week_number: Week number for naming
        
        Returns:
            Campaign ID
        """
        campaign_name = f"Week {week_number} - {difficulty} Campaign"
        start_date = datetime.now().isoformat()
        
        campaign_id = self.db.create_campaign(
            name=campaign_name,
            difficulty=difficulty,
            template_id=template_id,
            start_date=start_date,
            target_segment=target_segment
        )
        
        return campaign_id
    
    def run_weekly_simulation(self, week_number: int = 5) -> Dict:
        """
        Main scheduler function: Run weekly simulation
        This creates and launches campaigns based on automation rules
        
        Args:
            week_number: Current week number
        
        Returns:
            Dict with results of all campaigns launched
        """
        results = {
            'week': week_number,
            'campaigns_launched': [],
            'total_messages': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Get templates
        templates = self.db.get_all_templates()
        if not templates:
            return {'success': False, 'error': 'No templates available'}
        
        # Automation rules for Week 5
        # 1. Medium campaign to all users
        medium_template = next((t for t in templates if t['difficulty'] == 'Medium'), templates[0])
        campaign_all = self.schedule_weekly_campaign(
            template_id=medium_template['id'],
            difficulty='Medium',
            target_segment='all',
            week_number=week_number
        )
        
        launch_result_all = self.launch_campaign(campaign_all)
        if launch_result_all['success']:
            results['campaigns_launched'].append(launch_result_all)
            results['total_messages'] += launch_result_all['messages_sent']
        
        # 2. Extra campaign for high-risk users
        high_risk_users = self.db.get_users_by_risk_category('High')
        if high_risk_users:
            hard_template = next((t for t in templates if t['difficulty'] == 'Hard'), templates[0])
            campaign_high_risk = self.schedule_weekly_campaign(
                template_id=hard_template['id'],
                difficulty='Hard',
                target_segment='high_risk',
                week_number=week_number
            )
            
            launch_result_high = self.launch_campaign(campaign_high_risk)
            if launch_result_high['success']:
                results['campaigns_launched'].append(launch_result_high)
                results['total_messages'] += launch_result_high['messages_sent']
        
        results['success'] = True
        return results
    
    def complete_campaign(self, campaign_id: int) -> bool:
        """Mark a campaign as completed"""
        self.db.update_campaign_status(campaign_id, 'completed')
        self.db.update_campaign_metrics(campaign_id)
        return True
    
    def get_scheduled_campaigns(self) -> List[Dict]:
        """Get all scheduled campaigns"""
        all_campaigns = self.db.get_all_campaigns()
        return [c for c in all_campaigns if c['status'] == 'scheduled']
    
    def get_active_campaigns(self) -> List[Dict]:
        """Get all active campaigns"""
        all_campaigns = self.db.get_all_campaigns()
        return [c for c in all_campaigns if c['status'] == 'active']


class MetricsTracker:
    """Tracks and compares campaign metrics over time"""
    
    def __init__(self):
        self.db = Database()
    
    def get_campaign_summary(self, campaign_id: int) -> Dict:
        """Get comprehensive summary for a campaign"""
        campaign = self.db.get_campaign(campaign_id)
        metrics = self.db.get_campaign_metrics(campaign_id)
        
        if not campaign or not metrics:
            return {}
        
        return {
            'campaign_id': campaign_id,
            'name': campaign['name'],
            'difficulty': campaign['difficulty'],
            'status': campaign['status'],
            'start_date': campaign['start_date'],
            'metrics': {
                'total_sent': metrics['total_sent'],
                'click_rate': round(metrics['click_rate'], 2),
                'report_rate': round(metrics['report_rate'], 2),
                'training_completion_rate': round(metrics['training_completion_rate'], 2),
                'total_clicks': metrics['total_clicks'],
                'total_reports': metrics['total_reports']
            }
        }
    
    def get_trend_comparison(self) -> Dict:
        """
        Compare metrics across campaigns to show trends
        
        Returns:
            Dict with baseline and current metrics
        """
        all_metrics = self.db.get_all_metrics()
        
        if len(all_metrics) < 2:
            return {'error': 'Not enough campaigns for trend analysis'}
        
        # Sort by date
        sorted_metrics = sorted(all_metrics, key=lambda x: x['start_date'] or '')
        
        baseline = sorted_metrics[0]
        latest = sorted_metrics[-1]
        
        # Calculate high-risk specific metrics
        high_risk_campaigns = [m for m in sorted_metrics if 'high_risk' in m.get('name', '').lower()]
        
        trend_data = {
            'baseline': {
                'campaign': baseline['name'],
                'click_rate': round(baseline['click_rate'], 2),
                'report_rate': round(baseline['report_rate'], 2),
                'date': baseline['start_date']
            },
            'latest': {
                'campaign': latest['name'],
                'click_rate': round(latest['click_rate'], 2),
                'report_rate': round(latest['report_rate'], 2),
                'date': latest['start_date']
            },
            'improvement': {
                'click_rate_change': round(baseline['click_rate'] - latest['click_rate'], 2),
                'report_rate_change': round(latest['report_rate'] - baseline['report_rate'], 2)
            }
        }
        
        if high_risk_campaigns:
            high_risk_latest = high_risk_campaigns[-1]
            trend_data['high_risk_group'] = {
                'campaign': high_risk_latest['name'],
                'click_rate': round(high_risk_latest['click_rate'], 2),
                'report_rate': round(high_risk_latest['report_rate'], 2)
            }
        
        return trend_data
    
    def get_all_campaign_metrics(self) -> List[Dict]:
        """Get metrics for all campaigns in a formatted list"""
        all_metrics = self.db.get_all_metrics()
        
        formatted = []
        for m in all_metrics:
            formatted.append({
                'campaign': m['name'],
                'difficulty': m['difficulty'],
                'status': m['status'],
                'sent': m['total_sent'],
                'click_rate': f"{m['click_rate']:.1f}%",
                'report_rate': f"{m['report_rate']:.1f}%",
                'training_completion': f"{m['training_completion_rate']:.1f}%",
                'date': m['start_date']
            })
        
        return formatted


if __name__ == '__main__':
    # Test automation
    automation = CampaignAutomation()
    print("Campaign automation module loaded successfully!")
