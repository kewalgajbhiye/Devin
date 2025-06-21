"""
Database configuration and connection settings
"""

import sqlite3
import os
from pathlib import Path

class DatabaseConfig:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.connection_timeout = 30
        self.check_same_thread = False
        
    def get_connection(self):
        """Get database connection with proper configuration"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.connection_timeout,
            check_same_thread=self.check_same_thread
        )
        conn.row_factory = sqlite3.Row
        return conn
        
    def execute_script(self, script_path):
        """Execute SQL script file"""
        with open(script_path, 'r') as f:
            script = f.read()
        
        conn = self.get_connection()
        try:
            conn.executescript(script)
            conn.commit()
        finally:
            conn.close()

class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'business_data.db')
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def close_connection(self, conn: sqlite3.Connection):
        """Close database connection"""
        if conn:
            conn.close()
