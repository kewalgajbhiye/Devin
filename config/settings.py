"""
Application settings and configuration
"""

import os
from pathlib import Path

class AppSettings:
    def __init__(self):
        self.app_name = "Modern Business Management System"
        self.version = "1.0.0"
        self.company_name = "UMESH BALIRAM NIPANE"
        self.business_type = "Vegetable Merchants & Commission Agent"
        
        self.app_dir = Path(__file__).parent.parent
        self.data_dir = self.app_dir / "data"
        self.database_path = self.data_dir / "business_data.db"
        self.backup_dir = self.data_dir / "backups"
        self.reports_dir = self.data_dir / "reports"
        
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        self.window_width = 1200
        self.window_height = 800
        self.theme = "modern"
        
        self.colors = {
            'primary': '#2E86AB',      # Blue
            'secondary': '#A23B72',    # Purple
            'success': '#28A745',      # Green
            'warning': '#FFC107',      # Yellow
            'danger': '#DC3545',       # Red
            'info': '#17A2B8',         # Cyan
            'background': '#F8F9FA',   # Light gray
            'card': '#FFFFFF',         # White
            'text': '#212529',         # Dark gray
            'muted': '#6C757D'         # Muted gray
        }
        
        self.company_details = {
            'name': 'UMESH BALIRAM NIPANE',
            'business_type': 'Vegetable Merchants & Commission Agent',
            'address1': 'Shop No. 15, Gala No.5, Kalamna Sabji Market',
            'address2': 'Shop No.15, Mahatma Fule Sabji Market',
            'city': 'Nagpur',
            'jurisdiction': 'Subject to Nagpur Jurisdiction',
            'phone_umesh': '70202 70292',
            'phone_harish': '88882 12800',
            'market_closed': 'Friday Market Closed'
        }
