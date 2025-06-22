"""
Trial Balance Management
"""

import csv
from datetime import datetime
from database.queries import DatabaseQueries

class TrialBalanceManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.queries = DatabaseQueries(db_manager)
    
    def import_trial_balance_data(self, csv_file_path):
        """Import trial balance data from CSV file"""
        try:
            imported_count = 0
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    try:
                        trial_balance_data = {
                            'party_cd': row.get('PARTY_CD', ''),
                            'party_nm': row.get('PARTY_NM', ''),
                            'opening_balance': float(row.get('OPENING_BAL', 0)),
                            'debit_amount': float(row.get('DEBIT_AMT', 0)),
                            'credit_amount': float(row.get('CREDIT_AMT', 0)),
                            'closing_balance': float(row.get('CLOSING_BAL', 0)),
                            'balance_date': row.get('BAL_DATE', datetime.now().strftime('%Y-%m-%d'))
                        }
                        
                        if self.save_trial_balance_entry(trial_balance_data):
                            imported_count += 1
                            
                    except Exception as e:
                        print(f"Error importing trial balance record: {e}")
                        continue
            
            return imported_count
            
        except Exception as e:
            print(f"Error importing trial balance data: {e}")
            return 0
    
    def save_trial_balance_entry(self, trial_balance_data):
        """Save trial balance entry to database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO trial_balance 
                (party_cd, party_nm, opening_balance, debit_amount, credit_amount, 
                 closing_balance, balance_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                trial_balance_data['party_cd'],
                trial_balance_data['party_nm'],
                trial_balance_data['opening_balance'],
                trial_balance_data['debit_amount'],
                trial_balance_data['credit_amount'],
                trial_balance_data['closing_balance'],
                trial_balance_data['balance_date']
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error saving trial balance entry: {e}")
            return False
    
    def get_trial_balance_report(self, from_date=None, to_date=None):
        """Generate trial balance report"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM trial_balance"
            params = []
            
            if from_date and to_date:
                query += " WHERE balance_date BETWEEN ? AND ?"
                params = [from_date, to_date]
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Error generating trial balance report: {e}")
            return []
