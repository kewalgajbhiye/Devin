"""
Database models and schema definitions
"""

import sqlite3
from datetime import datetime, date
from pathlib import Path
import logging

class DatabaseManager:
    def __init__(self, db_path="business_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS company (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    address1 TEXT,
                    address2 TEXT,
                    city TEXT,
                    phone TEXT,
                    from_date DATE,
                    to_date DATE,
                    password TEXT,
                    directory TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parties (
                    party_cd TEXT PRIMARY KEY,
                    party_nm TEXT NOT NULL,
                    place TEXT,
                    phone TEXT,
                    bal_cd TEXT DEFAULT 'D',
                    ly_baln REAL DEFAULT 0,
                    ytd_dr REAL DEFAULT 0,
                    ytd_cr REAL DEFAULT 0,
                    created_date DATE DEFAULT CURRENT_DATE,
                    modified_date DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    it_cd TEXT PRIMARY KEY,
                    it_nm TEXT NOT NULL,
                    unit TEXT DEFAULT 'KG',
                    rate REAL DEFAULT 0,
                    category TEXT,
                    created_date DATE DEFAULT CURRENT_DATE,
                    modified_date DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_no INTEGER NOT NULL,
                    bill_date DATE NOT NULL,
                    party_cd TEXT NOT NULL,
                    it_cd TEXT NOT NULL,
                    qty REAL NOT NULL DEFAULT 0,
                    katta REAL DEFAULT 0,
                    tot_smt REAL DEFAULT 0,
                    rate REAL NOT NULL DEFAULT 0,
                    sal_amt REAL NOT NULL DEFAULT 0,
                    order_no TEXT,
                    order_dt DATE,
                    lr_no TEXT,
                    trans_cd TEXT,
                    agent_cd TEXT,
                    exp1 REAL DEFAULT 0,
                    exp2 REAL DEFAULT 0,
                    exp3 REAL DEFAULT 0,
                    exp4 REAL DEFAULT 0,
                    exp5 REAL DEFAULT 0,
                    cash REAL DEFAULT 0,
                    other REAL DEFAULT 0,
                    pkgs TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd),
                    FOREIGN KEY (it_cd) REFERENCES items (it_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_no INTEGER NOT NULL,
                    bill_date DATE NOT NULL,
                    party_cd TEXT NOT NULL,
                    it_cd TEXT NOT NULL,
                    qty REAL NOT NULL DEFAULT 0,
                    katta REAL DEFAULT 0,
                    tot_smt REAL DEFAULT 0,
                    rate REAL NOT NULL DEFAULT 0,
                    sal_amt REAL NOT NULL DEFAULT 0,
                    order_no TEXT,
                    order_dt DATE,
                    lr_no TEXT,
                    trans_cd TEXT,
                    agent_cd TEXT,
                    exp1 REAL DEFAULT 0,
                    exp2 REAL DEFAULT 0,
                    exp3 REAL DEFAULT 0,
                    exp4 REAL DEFAULT 0,
                    exp5 REAL DEFAULT 0,
                    cash REAL DEFAULT 0,
                    other REAL DEFAULT 0,
                    pkgs TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd),
                    FOREIGN KEY (it_cd) REFERENCES items (it_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vouch_date DATE NOT NULL,
                    vouch_no TEXT,
                    party_cd TEXT NOT NULL,
                    particulars TEXT,
                    dr_amt REAL DEFAULT 0,
                    cr_amt REAL DEFAULT 0,
                    balance REAL DEFAULT 0,
                    vouch_type TEXT,
                    ref_no TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cashbook (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vouch_date DATE NOT NULL,
                    vouch_no TEXT,
                    particulars TEXT,
                    dr_amt REAL DEFAULT 0,
                    cr_amt REAL DEFAULT 0,
                    balance REAL DEFAULT 0,
                    party_cd TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bankbook (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vouch_date DATE NOT NULL,
                    vouch_no TEXT,
                    particulars TEXT,
                    dr_amt REAL DEFAULT 0,
                    cr_amt REAL DEFAULT 0,
                    balance REAL DEFAULT 0,
                    party_cd TEXT,
                    bank_name TEXT,
                    cheque_no TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS journal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vouch_date DATE NOT NULL,
                    vouch_no TEXT,
                    party_cd TEXT NOT NULL,
                    particulars TEXT,
                    dr_amt REAL DEFAULT 0,
                    cr_amt REAL DEFAULT 0,
                    ref_no TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS receipts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_no INTEGER NOT NULL,
                    bill_date DATE NOT NULL,
                    party_cd TEXT NOT NULL,
                    amount REAL NOT NULL DEFAULT 0,
                    particulars TEXT,
                    payment_mode TEXT DEFAULT 'CASH',
                    cheque_no TEXT,
                    bank_name TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transport (
                    trans_cd TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    dest TEXT,
                    phone TEXT,
                    address TEXT,
                    created_date DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS packing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_no INTEGER,
                    it_cd TEXT,
                    packing_desc TEXT,
                    qty REAL DEFAULT 0,
                    FOREIGN KEY (it_cd) REFERENCES items (it_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_adjustment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adj_date DATE NOT NULL,
                    it_cd TEXT NOT NULL,
                    adj_qty REAL NOT NULL DEFAULT 0,
                    adj_type TEXT NOT NULL,
                    reason TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (it_cd) REFERENCES items (it_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lot_stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lot_no TEXT NOT NULL,
                    it_cd TEXT NOT NULL,
                    qty REAL NOT NULL DEFAULT 0,
                    rate REAL DEFAULT 0,
                    lot_date DATE NOT NULL,
                    expiry_date DATE,
                    status TEXT DEFAULT 'ACTIVE',
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (it_cd) REFERENCES items (it_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credit_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_no INTEGER NOT NULL,
                    bill_date DATE NOT NULL,
                    party_cd TEXT NOT NULL,
                    truck_no TEXT,
                    particulars TEXT,
                    description TEXT,
                    amount REAL NOT NULL DEFAULT 0,
                    tot_amt REAL NOT NULL DEFAULT 0,
                    it_cd TEXT,
                    qty REAL DEFAULT 0,
                    rate REAL DEFAULT 0,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd),
                    FOREIGN KEY (it_cd) REFERENCES items (it_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS debit_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_no INTEGER NOT NULL,
                    bill_date DATE NOT NULL,
                    party_cd TEXT NOT NULL,
                    truck_no TEXT,
                    particulars TEXT,
                    description TEXT,
                    amount REAL NOT NULL DEFAULT 0,
                    tot_amt REAL NOT NULL DEFAULT 0,
                    it_cd TEXT,
                    qty REAL DEFAULT 0,
                    rate REAL DEFAULT 0,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd),
                    FOREIGN KEY (it_cd) REFERENCES items (it_cd)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    agent_cd TEXT PRIMARY KEY,
                    agent_nm TEXT NOT NULL,
                    commission_rate REAL DEFAULT 0,
                    phone TEXT,
                    address TEXT,
                    created_date DATE DEFAULT CURRENT_DATE,
                    modified_date DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crate_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    party_cd TEXT NOT NULL,
                    total_crates INTEGER DEFAULT 0,
                    crates_given INTEGER DEFAULT 0,
                    crates_received INTEGER DEFAULT 0,
                    remaining_crates INTEGER DEFAULT 0,
                    crate_type TEXT DEFAULT 'Standard',
                    last_updated DATE DEFAULT CURRENT_DATE,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (party_cd) REFERENCES parties (party_cd)
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchases_bill_no ON purchases(bill_no)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases(bill_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchases_party ON purchases(party_cd)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_bill_no ON sales(bill_no)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(bill_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sales_party ON sales(party_cd)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ledger_party ON ledger(party_cd)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ledger_date ON ledger(vouch_date)')
            
            conn.commit()
            logging.info("Database initialized successfully")
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    def get_next_bill_number(self, table_name):
        """Get next bill number for purchases or sales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT MAX(bill_no) FROM {table_name}')
            result = cursor.fetchone()
            next_bill_no = (result[0] or 0) + 1
            return next_bill_no
        finally:
            conn.close()
    
    def backup_database(self, backup_path):
        """Create database backup"""
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return False
