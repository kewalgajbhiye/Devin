#!/usr/bin/env python3
"""
Modern Business Management System
Main application entry point
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import ModernBusinessApp
from database.models import DatabaseManager
from config.settings import AppSettings

def main():
    """Main application entry point"""
    try:
        settings = AppSettings()
        
        db_manager = DatabaseManager(settings.database_path)
        
        app = ModernBusinessApp(db_manager, settings)
        app.run()
        
    except Exception as e:
        messagebox.showerror("Application Error", f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
