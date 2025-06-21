"""
Purchase management business logic
"""

from datetime import datetime, date
from typing import List, Dict, Tuple
from database.queries import DatabaseQueries

class PurchaseManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.queries = DatabaseQueries(db_manager)
    
    def create_purchase_entry(self, bill_data: Dict, items: List[Dict]) -> Tuple[bool, str]:
        """Create new purchase entry with validation"""
        try:
            if not bill_data.get('bill_no'):
                return False, "Bill number is required"
            
            if not bill_data.get('party_cd'):
                return False, "Party code is required"
            
            if not items:
                return False, "At least one item is required"
            
            for item in items:
                if not item.get('it_cd'):
                    return False, "Item code is required for all items"
                if not item.get('qty') or float(item['qty']) <= 0:
                    return False, "Quantity must be greater than 0"
                if not item.get('rate') or float(item['rate']) <= 0:
                    return False, "Rate must be greater than 0"
                
                item['sal_amt'] = float(item['qty']) * float(item['rate'])
            
            return self.queries.save_purchase(bill_data, items)
            
        except Exception as e:
            return False, f"Error creating purchase entry: {e}"
    
    def get_next_bill_number(self) -> int:
        """Get next available bill number"""
        return self.queries.get_next_bill_number('purchases')
    
    def get_purchase_details(self, bill_no: int) -> List[Dict]:
        """Get purchase details by bill number"""
        return self.queries.get_purchase_by_bill_no(bill_no)
    
    def get_purchases_by_date(self, start_date: date, end_date: date) -> List[Dict]:
        """Get purchases within date range"""
        return self.queries.get_purchases_by_date_range(start_date, end_date)
    
    def validate_bill_number(self, bill_no: int) -> bool:
        """Check if bill number already exists"""
        existing = self.queries.get_purchase_by_bill_no(bill_no)
        return len(existing) == 0
