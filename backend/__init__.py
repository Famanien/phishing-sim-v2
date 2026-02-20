"""
Backend package for Phishing Simulation System
"""

from .firebase_database import FirebaseDatabase as Database, get_database
from .automation import CampaignAutomation, MetricsTracker

__all__ = ['Database', 'get_database', 'CampaignAutomation', 'MetricsTracker']
