"""
Database query operations and business logic
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

class DatabaseQueries:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_all_parties(self) -> List[Dict]:
        """Get all parties"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT party_cd, party_nm, place, phone, bal_cd, ly_baln, ytd_dr, ytd_cr
                FROM parties 
                ORDER BY party_nm
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def search_parties(self, search_term: str) -> List[Dict]:
        """Search parties by name or code"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT party_cd, party_nm, place, phone
                FROM parties 
                WHERE party_nm LIKE ? OR party_cd LIKE ?
                ORDER BY party_nm
                LIMIT 20
            ''', (f'%{search_term}%', f'%{search_term}%'))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_party_by_code(self, party_cd: str) -> Optional[Dict]:
        """Get party by code"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM parties WHERE party_cd = ?
            ''', (party_cd,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def save_party(self, party_data: Dict) -> bool:
        """Save or update party"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO parties 
                (party_cd, party_nm, place, phone, bal_cd, ly_baln, ytd_dr, ytd_cr, modified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_DATE)
            ''', (
                party_data['party_cd'],
                party_data['party_nm'],
                party_data.get('place', ''),
                party_data.get('phone', ''),
                party_data.get('bal_cd', 'D'),
                party_data.get('ly_baln', 0),
                party_data.get('ytd_dr', 0),
                party_data.get('ytd_cr', 0)
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving party: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_items(self) -> List[Dict]:
        """Get all items"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT it_cd, it_nm, unit, rate, category
                FROM items 
                ORDER BY it_nm
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def search_items(self, search_term: str) -> List[Dict]:
        """Search items by name or code"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT it_cd, it_nm, unit, rate
                FROM items 
                WHERE it_nm LIKE ? OR it_cd LIKE ?
                ORDER BY it_nm
                LIMIT 20
            ''', (f'%{search_term}%', f'%{search_term}%'))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_item_by_code(self, it_cd: str) -> Optional[Dict]:
        """Get item by code"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM items WHERE it_cd = ?
            ''', (it_cd,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def save_item(self, item_data: Dict) -> bool:
        """Save or update item"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO items 
                (it_cd, it_nm, unit, rate, category, modified_date)
                VALUES (?, ?, ?, ?, ?, CURRENT_DATE)
            ''', (
                item_data['it_cd'],
                item_data['it_nm'],
                item_data.get('unit', 'KG'),
                item_data.get('rate', 0),
                item_data.get('category', '')
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving item: {e}")
            return False
        finally:
            conn.close()
    
    def save_purchase(self, purchase_data: Dict, items: List[Dict]) -> Tuple[bool, str]:
        """Save purchase with items"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM purchases WHERE bill_no = ?', (purchase_data['bill_no'],))
            if cursor.fetchone()[0] > 0:
                return False, "Bill number already exists"
            
            for item in items:
                cursor.execute('''
                    INSERT INTO purchases 
                    (bill_no, bill_date, party_cd, it_cd, qty, katta, tot_smt, rate, sal_amt, 
                     order_no, order_dt, lr_no, trans_cd, agent_cd, exp1, exp2, exp3, exp4, exp5, cash, other, pkgs)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    purchase_data['bill_no'],
                    purchase_data['bill_date'],
                    purchase_data['party_cd'],
                    item['it_cd'],
                    item['qty'],
                    item.get('katta', 0),
                    item.get('tot_smt', 0),
                    item['rate'],
                    item['sal_amt'],
                    purchase_data.get('order_no', ''),
                    purchase_data.get('order_dt'),
                    purchase_data.get('lr_no', ''),
                    purchase_data.get('trans_cd', ''),
                    purchase_data.get('agent_cd', ''),
                    purchase_data.get('exp1', 0),
                    purchase_data.get('exp2', 0),
                    purchase_data.get('exp3', 0),
                    purchase_data.get('exp4', 0),
                    purchase_data.get('exp5', 0),
                    purchase_data.get('cash', 0),
                    purchase_data.get('other', 0),
                    item.get('pkgs', '')
                ))
            
            conn.commit()
            return True, "Purchase saved successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error saving purchase: {e}"
        finally:
            conn.close()
    
    def get_all_cashbook_entries(self) -> List[Dict]:
        """Get all cash book entries"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT c.*, p.party_nm 
                FROM cashbook c
                LEFT JOIN parties p ON c.party_cd = p.party_cd
                ORDER BY c.vouch_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_cashbook_entry(self, entry_data: Dict) -> bool:
        """Save cash book entry"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO cashbook 
                (vouch_date, vouch_no, particulars, dr_amt, cr_amt, balance, party_cd)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_data['vouch_date'],
                entry_data.get('vouch_no', ''),
                entry_data['particulars'],
                entry_data.get('dr_amt', 0),
                entry_data.get('cr_amt', 0),
                entry_data.get('balance', 0),
                entry_data.get('party_cd', '')
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving cash book entry: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_bankbook_entries(self) -> List[Dict]:
        """Get all bank book entries"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT b.*, p.party_nm 
                FROM bankbook b
                LEFT JOIN parties p ON b.party_cd = p.party_cd
                ORDER BY b.vouch_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_bankbook_entry(self, entry_data: Dict) -> bool:
        """Save bank book entry"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO bankbook 
                (vouch_date, vouch_no, particulars, dr_amt, cr_amt, balance, party_cd, bank_name, cheque_no)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_data['vouch_date'],
                entry_data.get('vouch_no', ''),
                entry_data['particulars'],
                entry_data.get('dr_amt', 0),
                entry_data.get('cr_amt', 0),
                entry_data.get('balance', 0),
                entry_data.get('party_cd', ''),
                entry_data.get('bank_name', ''),
                entry_data.get('cheque_no', '')
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving bank book entry: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_journal_entries(self) -> List[Dict]:
        """Get all journal entries"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT j.*, p.party_nm 
                FROM journal j
                LEFT JOIN parties p ON j.party_cd = p.party_cd
                ORDER BY j.vouch_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_journal_entry(self, entry_data: Dict) -> bool:
        """Save journal entry"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO journal 
                (vouch_date, vouch_no, party_cd, particulars, dr_amt, cr_amt, ref_no)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_data['vouch_date'],
                entry_data.get('vouch_no', ''),
                entry_data['party_cd'],
                entry_data['particulars'],
                entry_data.get('dr_amt', 0),
                entry_data.get('cr_amt', 0),
                entry_data.get('ref_no', '')
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving journal entry: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_receipts(self) -> List[Dict]:
        """Get all receipts"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT r.*, p.party_nm 
                FROM receipts r
                LEFT JOIN parties p ON r.party_cd = p.party_cd
                ORDER BY r.bill_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_receipt(self, receipt_data: Dict) -> bool:
        """Save receipt"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO receipts 
                (bill_no, bill_date, party_cd, amount, particulars, payment_mode, cheque_no, bank_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                receipt_data['bill_no'],
                receipt_data['bill_date'],
                receipt_data['party_cd'],
                receipt_data['amount'],
                receipt_data.get('particulars', ''),
                receipt_data.get('payment_mode', 'CASH'),
                receipt_data.get('cheque_no', ''),
                receipt_data.get('bank_name', '')
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving receipt: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_stock_adjustments(self) -> List[Dict]:
        """Get all stock adjustments"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT s.*, i.it_nm 
                FROM stock_adjustment s
                LEFT JOIN items i ON s.it_cd = i.it_cd
                ORDER BY s.adj_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_stock_adjustment(self, adj_data: Dict) -> bool:
        """Save stock adjustment"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO stock_adjustment 
                (adj_date, it_cd, adj_qty, adj_type, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                adj_data['adj_date'],
                adj_data['it_cd'],
                adj_data['adj_qty'],
                adj_data['adj_type'],
                adj_data.get('reason', '')
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving stock adjustment: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_lot_stock(self) -> List[Dict]:
        """Get all lot stock"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT l.*, i.it_nm 
                FROM lot_stock l
                LEFT JOIN items i ON l.it_cd = i.it_cd
                ORDER BY l.lot_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_lot_stock(self, lot_data: Dict) -> bool:
        """Save lot stock"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO lot_stock 
                (lot_no, it_cd, qty, rate, lot_date, expiry_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                lot_data['lot_no'],
                lot_data['it_cd'],
                lot_data['qty'],
                lot_data['rate'],
                lot_data['lot_date'],
                lot_data.get('expiry_date'),
                lot_data.get('status', 'ACTIVE')
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving lot stock: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_transports(self) -> List[Dict]:
        """Get all transport companies"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT * FROM transport ORDER BY name
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_transport(self, transport_data: Dict) -> bool:
        """Save transport company"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO transport 
                (trans_cd, name, dest, phone, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                transport_data['trans_cd'],
                transport_data['name'],
                transport_data.get('dest', ''),
                transport_data.get('phone', ''),
                transport_data.get('address', '')
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving transport: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_agents(self) -> List[Dict]:
        """Get all agents"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT * FROM agents ORDER BY agent_nm
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_agent(self, agent_data: Dict) -> bool:
        """Save agent"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO agents 
                (agent_cd, agent_nm, commission_rate, phone, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                agent_data['agent_cd'],
                agent_data['agent_nm'],
                agent_data.get('commission_rate', 0),
                agent_data.get('phone', ''),
                agent_data.get('address', '')
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving agent: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_credit_notes(self) -> List[Dict]:
        """Get all credit notes"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT c.*, p.party_nm, i.it_nm 
                FROM credit_notes c
                LEFT JOIN parties p ON c.party_cd = p.party_cd
                LEFT JOIN items i ON c.it_cd = i.it_cd
                ORDER BY c.bill_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_credit_note(self, note_data: Dict) -> bool:
        """Save credit note"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO credit_notes 
                (bill_no, bill_date, party_cd, truck_no, particulars, description, amount, tot_amt, it_cd, qty, rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                note_data['bill_no'],
                note_data['bill_date'],
                note_data['party_cd'],
                note_data.get('truck_no', ''),
                note_data.get('particulars', ''),
                note_data.get('description', ''),
                note_data['amount'],
                note_data['tot_amt'],
                note_data.get('it_cd', ''),
                note_data.get('qty', 0),
                note_data.get('rate', 0)
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving credit note: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_debit_notes(self) -> List[Dict]:
        """Get all debit notes"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT d.*, p.party_nm, i.it_nm 
                FROM debit_notes d
                LEFT JOIN parties p ON d.party_cd = p.party_cd
                LEFT JOIN items i ON d.it_cd = i.it_cd
                ORDER BY d.bill_date DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_debit_note(self, note_data: Dict) -> bool:
        """Save debit note"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO debit_notes 
                (bill_no, bill_date, party_cd, truck_no, particulars, description, amount, tot_amt, it_cd, qty, rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                note_data['bill_no'],
                note_data['bill_date'],
                note_data['party_cd'],
                note_data.get('truck_no', ''),
                note_data.get('particulars', ''),
                note_data.get('description', ''),
                note_data['amount'],
                note_data['tot_amt'],
                note_data.get('it_cd', ''),
                note_data.get('qty', 0),
                note_data.get('rate', 0)
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving debit note: {e}")
            return False
        finally:
            conn.close()
    
    def get_purchase_by_bill_no(self, bill_no) -> List[Dict]:
        """Get purchase details by bill number"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT p.*, pt.party_nm, pt.place, pt.phone, i.it_nm, i.unit
                FROM purchases p
                LEFT JOIN parties pt ON p.party_cd = pt.party_cd
                LEFT JOIN items i ON p.it_cd = i.it_cd
                WHERE p.bill_no = ?
                ORDER BY p.id
            ''', (str(bill_no),))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_sales_by_bill_no(self, bill_no) -> List[Dict]:
        """Get sales details by bill number"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT s.*, pt.party_nm, pt.place, pt.phone, i.it_nm, i.unit
                FROM sales s
                LEFT JOIN parties pt ON s.party_cd = pt.party_cd
                LEFT JOIN items i ON s.it_cd = i.it_cd
                WHERE s.bill_no = ?
                ORDER BY s.id
            ''', (str(bill_no),))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_purchases_by_date_range(self, start_date: date, end_date: date) -> List[Dict]:
        """Get purchases by date range"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT p.bill_no, p.bill_date, pt.party_nm, SUM(p.sal_amt) as total_amount
                FROM purchases p
                LEFT JOIN parties pt ON p.party_cd = pt.party_cd
                WHERE p.bill_date BETWEEN ? AND ?
                GROUP BY p.bill_no, p.bill_date, pt.party_nm
                ORDER BY p.bill_date DESC, p.bill_no DESC
            ''', (start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_next_bill_number(self, table_name: str) -> int:
        """Get next bill number for purchases or sales"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT MAX(bill_no) FROM {table_name}')
            result = cursor.fetchone()
            return (result[0] or 0) + 1
        finally:
            conn.close()
    
    def save_sale(self, sale_data: Dict, items: List[Dict]) -> Tuple[bool, str]:
        """Save sales entry with items"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM sales WHERE bill_no = ?', (sale_data['bill_no'],))
            if cursor.fetchone()[0] > 0:
                return False, "Bill number already exists"
            
            for item in items:
                cursor.execute('''
                    INSERT INTO sales 
                    (bill_no, bill_date, party_cd, it_cd, qty, rate, sal_amt)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sale_data['bill_no'],
                    sale_data['bill_date'],
                    sale_data['party_cd'],
                    item['it_cd'],
                    item['qty'],
                    item['rate'],
                    item['sal_amt']
                ))
            
            conn.commit()
            return True, "Sale saved successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error saving sale: {e}"
        finally:
            conn.close()
    
    def get_all_purchases(self) -> List[Dict]:
        """Get all purchases"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT p.bill_no, p.bill_date, pt.party_nm, SUM(p.sal_amt) as total_amount
                FROM purchases p
                LEFT JOIN parties pt ON p.party_cd = pt.party_cd
                GROUP BY p.bill_no, p.bill_date, pt.party_nm
                ORDER BY p.bill_date DESC, p.bill_no DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_all_sales(self) -> List[Dict]:
        """Get all sales"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT s.bill_no, s.bill_date, pt.party_nm, SUM(s.sal_amt) as total_amount
                FROM sales s
                LEFT JOIN parties pt ON s.party_cd = pt.party_cd
                GROUP BY s.bill_no, s.bill_date, pt.party_nm
                ORDER BY s.bill_date DESC, s.bill_no DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_sales_by_date_range(self, start_date: date, end_date: date) -> List[Dict]:
        """Get sales by date range"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT s.bill_no, s.bill_date, pt.party_nm, SUM(s.sal_amt) as total_amount
                FROM sales s
                LEFT JOIN parties pt ON s.party_cd = pt.party_cd
                WHERE s.bill_date BETWEEN ? AND ?
                GROUP BY s.bill_no, s.bill_date, pt.party_nm
                ORDER BY s.bill_date DESC, s.bill_no DESC
            ''', (start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_stock_report(self) -> List[Dict]:
        """Get stock report"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT i.it_cd, i.it_nm, i.unit, i.rate,
                       COALESCE(SUM(p.qty), 0) as purchase_qty,
                       COALESCE(SUM(s.qty), 0) as sales_qty,
                       COALESCE(SUM(p.qty), 0) - COALESCE(SUM(s.qty), 0) as stock_qty
                FROM items i
                LEFT JOIN purchases p ON i.it_cd = p.it_cd
                LEFT JOIN sales s ON i.it_cd = s.it_cd
                GROUP BY i.it_cd, i.it_nm, i.unit, i.rate
                ORDER BY i.it_nm
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_party_ledger(self, party_cd: str) -> List[Dict]:
        """Get party ledger"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            ledger_entries = []
            
            # Get purchases
            cursor.execute('''
                SELECT bill_date as date, 'Purchase' as type, bill_no, sal_amt as amount
                FROM purchases WHERE party_cd = ?
            ''', (party_cd,))
            ledger_entries.extend([dict(row) for row in cursor.fetchall()])
            
            cursor.execute('''
                SELECT bill_date as date, 'Sales' as type, bill_no, sal_amt as amount
                FROM sales WHERE party_cd = ?
            ''', (party_cd,))
            ledger_entries.extend([dict(row) for row in cursor.fetchall()])
            
            cursor.execute('''
                SELECT bill_date as date, 'Receipt' as type, bill_no, amount
                FROM receipts WHERE party_cd = ?
            ''', (party_cd,))
            ledger_entries.extend([dict(row) for row in cursor.fetchall()])
            
            ledger_entries.sort(key=lambda x: x['date'])
            return ledger_entries
        finally:
            conn.close()
    
    def get_trial_balance(self) -> List[Dict]:
        """Get trial balance"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT p.party_cd, p.party_nm,
                       COALESCE(SUM(pur.sal_amt), 0) as purchase_amount,
                       COALESCE(SUM(sal.sal_amt), 0) as sales_amount,
                       COALESCE(SUM(rec.amount), 0) as receipt_amount,
                       (COALESCE(SUM(pur.sal_amt), 0) - COALESCE(SUM(sal.sal_amt), 0) - COALESCE(SUM(rec.amount), 0)) as balance
                FROM parties p
                LEFT JOIN purchases pur ON p.party_cd = pur.party_cd
                LEFT JOIN sales sal ON p.party_cd = sal.party_cd
                LEFT JOIN receipts rec ON p.party_cd = rec.party_cd
                GROUP BY p.party_cd, p.party_nm
                HAVING balance != 0
                ORDER BY p.party_nm
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def search_agents(self, search_term):
        """Search agents by name or code"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM agents 
                WHERE agent_nm LIKE ? OR agent_cd LIKE ?
                ORDER BY agent_nm
            ''', (f'%{search_term}%', f'%{search_term}%'))
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
        except Exception as e:
            print(f"Error searching agents: {e}")
            return []
    
    def get_item_purchases(self, item_code: str) -> List[Dict]:
        """Get all purchases for a specific item"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT qty, rate, sal_amt FROM purchases 
                WHERE it_cd = ?
            ''', (item_code,))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting item purchases: {e}")
            return []
    
    def get_item_sales(self, item_code: str) -> List[Dict]:
        """Get all sales for a specific item"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT qty, rate, sal_amt FROM sales 
                WHERE it_cd = ?
            ''', (item_code,))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting item sales: {e}")
            return []
        finally:
            conn.close()
    
    def get_sales_bill_summary(self, bill_no) -> Dict:
        """Get consolidated sales bill summary by bill number"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT s.bill_no, s.bill_date, pt.party_nm, pt.place, pt.phone,
                       SUM(s.sal_amt) as total_amount, COUNT(*) as item_count,
                       s.order_no, s.lr_no, s.trans_cd, s.agent_cd,
                       SUM(s.exp1) as exp1, SUM(s.exp2) as exp2, SUM(s.exp3) as exp3,
                       SUM(s.exp4) as exp4, SUM(s.exp5) as exp5, SUM(s.cash) as cash
                FROM sales s
                LEFT JOIN parties pt ON s.party_cd = pt.party_cd
                WHERE s.bill_no = ?
                GROUP BY s.bill_no, s.bill_date, pt.party_nm, pt.place, pt.phone,
                         s.order_no, s.lr_no, s.trans_cd, s.agent_cd
            ''', (str(bill_no),))
            result = cursor.fetchone()
            return dict(result) if result else {}
        finally:
            conn.close()
    
    def get_purchase_bill_summary(self, bill_no) -> Dict:
        """Get consolidated purchase bill summary by bill number"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT p.bill_no, p.bill_date, pt.party_nm, pt.place, pt.phone,
                       SUM(p.sal_amt) as total_amount, COUNT(*) as item_count,
                       p.order_no, p.lr_no, p.trans_cd, p.agent_cd,
                       SUM(p.exp1) as exp1, SUM(p.exp2) as exp2, SUM(p.exp3) as exp3,
                       SUM(p.exp4) as exp4, SUM(p.exp5) as exp5, SUM(p.cash) as cash
                FROM purchases p
                LEFT JOIN parties pt ON p.party_cd = pt.party_cd
                WHERE p.bill_no = ?
                GROUP BY p.bill_no, p.bill_date, pt.party_nm, pt.place, pt.phone,
                         p.order_no, p.lr_no, p.trans_cd, p.agent_cd
            ''', (str(bill_no),))
            result = cursor.fetchone()
            return dict(result) if result else {}
        finally:
            conn.close()
    
    def get_crate_management_by_party(self, party_cd: str) -> Dict:
        """Get crate management data for a party"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT cm.*, pt.party_nm 
                FROM crate_management cm
                LEFT JOIN parties pt ON cm.party_cd = pt.party_cd
                WHERE cm.party_cd = ?
            ''', (party_cd,))
            result = cursor.fetchone()
            return dict(result) if result else {}
        finally:
            conn.close()
    
    def get_all_crate_management(self) -> List[Dict]:
        """Get all crate management records"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT cm.*, pt.party_nm 
                FROM crate_management cm
                LEFT JOIN parties pt ON cm.party_cd = pt.party_cd
                ORDER BY pt.party_nm
            ''')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def save_crate_management(self, crate_data: Dict) -> bool:
        """Save or update crate management data"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            remaining = crate_data['total_crates'] - crate_data['crates_given'] + crate_data['crates_received']
            
            cursor.execute('SELECT COUNT(*) FROM crate_management WHERE party_cd = ?', (crate_data['party_cd'],))
            if cursor.fetchone()[0] > 0:
                cursor.execute('''
                    UPDATE crate_management 
                    SET total_crates = ?, crates_given = ?, crates_received = ?, 
                        remaining_crates = ?, crate_type = ?, last_updated = CURRENT_DATE
                    WHERE party_cd = ?
                ''', (crate_data['total_crates'], crate_data['crates_given'], 
                      crate_data['crates_received'], remaining, crate_data['crate_type'], 
                      crate_data['party_cd']))
            else:
                cursor.execute('''
                    INSERT INTO crate_management 
                    (party_cd, total_crates, crates_given, crates_received, remaining_crates, crate_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (crate_data['party_cd'], crate_data['total_crates'], 
                      crate_data['crates_given'], crate_data['crates_received'], 
                      remaining, crate_data['crate_type']))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving crate management: {e}")
            return False
        finally:
            conn.close()
    
    def update_purchase(self, bill_no: int, purchase_data: Dict, items: List[Dict]) -> Tuple[bool, str]:
        """Update existing purchase entry"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM purchases WHERE bill_no = ?', (bill_no,))
            
            for item in items:
                cursor.execute('''
                    INSERT INTO purchases 
                    (bill_no, bill_date, party_cd, it_cd, qty, rate, sal_amt, 
                     exp1, exp2, exp3, exp4, exp5, cash, order_no, lr_no, trans_cd, agent_cd)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill_no, purchase_data['bill_date'], purchase_data['party_cd'],
                    item['it_cd'], item['qty'], item['rate'], item['sal_amt'],
                    purchase_data.get('exp1', 0), purchase_data.get('exp2', 0),
                    purchase_data.get('exp3', 0), purchase_data.get('exp4', 0),
                    purchase_data.get('exp5', 0), purchase_data.get('cash', 0),
                    purchase_data.get('order_no', ''), purchase_data.get('lr_no', ''),
                    purchase_data.get('trans_cd', ''), purchase_data.get('agent_cd', '')
                ))
            
            conn.commit()
            return True, "Purchase updated successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error updating purchase: {e}"
        finally:
            conn.close()
    
    def update_sale(self, bill_no: int, sale_data: Dict, items: List[Dict]) -> Tuple[bool, str]:
        """Update existing sales entry"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM sales WHERE bill_no = ?', (bill_no,))
            
            for item in items:
                cursor.execute('''
                    INSERT INTO sales 
                    (bill_no, bill_date, party_cd, it_cd, qty, rate, sal_amt,
                     exp1, exp2, exp3, exp4, exp5, cash, order_no, lr_no, trans_cd, agent_cd)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill_no, sale_data['bill_date'], sale_data['party_cd'],
                    item['it_cd'], item['qty'], item['rate'], item['sal_amt'],
                    sale_data.get('exp1', 0), sale_data.get('exp2', 0),
                    sale_data.get('exp3', 0), sale_data.get('exp4', 0),
                    sale_data.get('exp5', 0), sale_data.get('cash', 0),
                    sale_data.get('order_no', ''), sale_data.get('lr_no', ''),
                    sale_data.get('trans_cd', ''), sale_data.get('agent_cd', '')
                ))
            
            conn.commit()
            return True, "Sale updated successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error updating sale: {e}"
        finally:
            conn.close()
