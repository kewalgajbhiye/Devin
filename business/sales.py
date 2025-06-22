"""
Sales management business logic
"""

from datetime import datetime, date
from typing import List, Dict, Tuple
from database.queries import DatabaseQueries

class SalesManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.queries = DatabaseQueries(db_manager)
    
    def create_sales_entry(self, bill_data: Dict, items: List[Dict]) -> Tuple[bool, str]:
        """Create new sales entry with validation"""
        try:
            if not bill_data.get('bill_no'):
                return False, "Bill number is required"
            
            if not bill_data.get('party_cd'):
                return False, "Party code is required"
            
            if not items:
                return False, "At least one item is required"
            
            for item in items:
                if not item.get('item_code'):
                    return False, "Item code is required for all items"
                if not item.get('quantity') or float(item['quantity']) <= 0:
                    return False, "Quantity must be greater than 0"
                if not item.get('rate') or float(item['rate']) <= 0:
                    return False, "Rate must be greater than 0"
                    
                item['amount'] = float(item['quantity']) * float(item['rate'])
            
            return self.queries.save_sale(bill_data, items)
            
        except Exception as e:
            return False, f"Error creating sales entry: {e}"
    
    def update_sales_entry(self, bill_no: int, bill_data: Dict, items: List[Dict]) -> Tuple[bool, str]:
        """Update existing sales entry"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("DELETE FROM sales WHERE bill_no = ?", (bill_no,))
                
                for item in items:
                    cursor.execute("""
                        INSERT INTO sales (bill_no, bill_date, party_cd, party_nm, it_cd, it_nm, 
                                         qty, rate, sal_amt, transport, vehicle, remarks,
                                         exp1, exp2, exp3, exp4, exp5, cash, total_amount)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        bill_data['bill_no'], bill_data['bill_dt'], bill_data['party_cd'],
                        bill_data.get('party_nm', ''), item['item_code'], item['item_name'],
                        item['quantity'], item['rate'], item['amount'],
                        bill_data.get('transport', ''), bill_data.get('vehicle_no', ''),
                        bill_data.get('remarks', ''), bill_data.get('exp1', 0),
                        bill_data.get('exp2', 0), bill_data.get('exp3', 0),
                        bill_data.get('exp4', 0), bill_data.get('exp5', 0),
                        bill_data.get('cash', 0), bill_data.get('total_amount', 0)
                    ))
                
                conn.commit()
                return True, "Sales entry updated successfully"
                
            except Exception as e:
                conn.rollback()
                return False, f"Database error: {e}"
            finally:
                conn.close()
                
        except Exception as e:
            return False, f"Error updating sales entry: {e}"
    
    def get_next_bill_number(self) -> int:
        """Get next available bill number"""
        return self.queries.get_next_bill_number('sales')
    
    def get_sales_details(self, bill_no: int) -> List[Dict]:
        """Get sales details by bill number"""
        return self.queries.get_sales_by_bill_no(bill_no)
    
    def get_sales_by_date(self, start_date: date, end_date: date) -> List[Dict]:
        """Get sales within date range"""
        return self.queries.get_sales_by_date_range(start_date, end_date)
    
    def validate_bill_number(self, bill_no: int) -> bool:
        """Check if bill number already exists"""
        existing = self.queries.get_sales_by_bill_no(bill_no)
        return len(existing) == 0
