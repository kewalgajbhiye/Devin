"""
Business utility functions
"""

from datetime import datetime, date
import re

def validate_party_code(party_cd: str) -> bool:
    """Validate party code format"""
    if not party_cd or len(party_cd.strip()) == 0:
        return False
    return len(party_cd.strip()) <= 10

def validate_item_code(it_cd: str) -> bool:
    """Validate item code format"""
    if not it_cd or len(it_cd.strip()) == 0:
        return False
    return len(it_cd.strip()) <= 10

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return True
    phone = re.sub(r'[^\d]', '', phone)
    return len(phone) >= 10

def format_currency(amount: float) -> str:
    """Format currency in Indian format"""
    return f"₹{amount:,.2f}"

def parse_date(date_str: str) -> date:
    """Parse date string in various formats"""
    if not date_str:
        return date.today()
    
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return date.today()

def calculate_amount(qty: float, rate: float) -> float:
    """Calculate amount from quantity and rate"""
    return round(float(qty) * float(rate), 2)

def get_financial_year(dt: date = None) -> str:
    """Get financial year string (e.g., '2024-25')"""
    if dt is None:
        dt = date.today()
    
    if dt.month >= 4:
        return f"{dt.year}-{str(dt.year + 1)[-2:]}"
    else:
        return f"{dt.year - 1}-{str(dt.year)[-2:]}"
