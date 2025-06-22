"""
Dashboard cards component for main interface
"""

import tkinter as tk
from tkinter import ttk

class DashboardCards:
    def __init__(self, parent, settings, main_app):
        self.parent = parent
        self.settings = settings
        self.main_app = main_app
        self.colors = settings.colors
    
    def create_cards(self):
        """Create dashboard cards"""
        cards_container = ttk.Frame(self.parent)
        cards_container.pack(fill='both', expand=True, pady=10)
        
        top_row = ttk.Frame(cards_container)
        top_row.pack(fill='x', pady=(0, 10))
        
        bottom_row = ttk.Frame(cards_container)
        bottom_row.pack(fill='x')
        
        self.create_purchase_card(top_row)
        self.create_sales_card(top_row)
        self.create_inventory_card(top_row)
        
        self.create_accounting_card(bottom_row)
        self.create_documents_card(bottom_row)
        self.create_reports_card(bottom_row)
        self.create_settings_card(bottom_row)
    
    def create_purchase_card(self, parent):
        """Create purchase management card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        title = ttk.Label(card, text="🛒 Purchase Management", style='Title.TLabel')
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="Manage purchase entries, bills, and supplier transactions",
                        font=('Arial', 9),
                        background=self.colors['card'],
                        foreground=self.colors['muted'],
                        wraplength=200)
        desc.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=(0, 10))
        
        ttk.Button(btn_frame, 
                  text="New Purchase Entry", 
                  command=self.main_app.open_purchase_form,
                  style='Primary.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Print Purchase Bill", 
                  command=self.main_app.print_purchase_bill,
                  style='Modern.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Print Purchase Entry", 
                  command=self.main_app.print_purchase_entry,
                  style='Modern.TButton').pack(pady=2, fill='x')
    
    def create_sales_card(self, parent):
        """Create sales management card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side='left', fill='both', expand=True, padx=5)
        
        title = ttk.Label(card, text="💰 Sales Management", style='Title.TLabel')
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="Handle sales transactions, invoices, and customer orders",
                        font=('Arial', 9),
                        background=self.colors['card'],
                        foreground=self.colors['muted'],
                        wraplength=200)
        desc.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=(0, 10))
        
        ttk.Button(btn_frame, 
                  text="New Sales Entry", 
                  command=self.main_app.open_sales_form,
                  style='Success.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="SALEPATTI Entry", 
                  command=self.main_app.open_salepatti_form,
                  style='Warning.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Print Sales Bill", 
                  command=self.main_app.print_sales_bill,
                  style='Success.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Print Sales Entry", 
                  command=self.main_app.print_sales_entry,
                  style='Modern.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Sales Reports", 
                  command=self.main_app.show_sales_reports,
                  style='Modern.TButton').pack(pady=2, fill='x')
    
    def create_inventory_card(self, parent):
        """Create inventory management card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        title = ttk.Label(card, text="📦 Inventory", style='Title.TLabel')
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="Track stock levels, manage items, and monitor inventory",
                        font=('Arial', 9),
                        background=self.colors['card'],
                        foreground=self.colors['muted'],
                        wraplength=200)
        desc.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=(0, 10))
        
        ttk.Button(btn_frame, 
                  text="Manage Items", 
                  command=self.main_app.open_item_form,
                  style='Primary.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Stock Adjustment", 
                  command=self.main_app.open_stock_adjustment_form,
                  style='Primary.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Lot Management", 
                  command=self.main_app.open_lot_management_form,
                  style='Modern.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Stock Report", 
                  command=self.main_app.show_stock_report,
                  style='Success.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Crate Management", 
                  command=self.main_app.open_crate_management_form,
                  style='Warning.TButton').pack(pady=2, fill='x')
    
    def create_accounting_card(self, parent):
        """Create accounting card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        title = ttk.Label(card, text="📊 Accounting", style='Title.TLabel')
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="Ledger management, cash/bank books, and financial reports",
                        font=('Arial', 9),
                        background=self.colors['card'],
                        foreground=self.colors['muted'],
                        wraplength=200)
        desc.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=(0, 10))
        
        ttk.Button(btn_frame, 
                  text="Cash Book Entry", 
                  command=self.main_app.open_cashbook_form,
                  style='Primary.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Bank Book Entry", 
                  command=self.main_app.open_bankbook_form,
                  style='Primary.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Journal Entry", 
                  command=self.main_app.open_journal_form,
                  style='Modern.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Receipt Management", 
                  command=self.main_app.open_receipt_form,
                  style='Modern.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Ledger Reports", 
                  command=self.main_app.show_ledger_reports,
                  style='Success.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Trial Balance", 
                  command=self.main_app.show_trial_balance,
                  style='Success.TButton').pack(pady=2, fill='x')
    
    def create_reports_card(self, parent):
        """Create reports card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side='left', fill='both', expand=True, padx=5)
        
        title = ttk.Label(card, text="📈 Reports", style='Title.TLabel')
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="Generate business reports, analytics, and summaries",
                        font=('Arial', 9),
                        background=self.colors['card'],
                        foreground=self.colors['muted'],
                        wraplength=200)
        desc.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=(0, 10))
        
        ttk.Button(btn_frame, 
                  text="Purchase Reports", 
                  command=self.main_app.show_purchase_reports,
                  style='Modern.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Party Statements", 
                  command=self.main_app.show_party_statements,
                  style='Modern.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Print All Reports", 
                  command=self.main_app.open_print_all_reports_form,
                  style='Success.TButton').pack(pady=2, fill='x')
    
    def create_settings_card(self, parent):
        """Create settings card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        title = ttk.Label(card, text="⚙️ Settings", style='Title.TLabel')
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="Manage parties, system settings, and data migration",
                        font=('Arial', 9),
                        background=self.colors['card'],
                        foreground=self.colors['muted'],
                        wraplength=200)
        desc.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=(0, 10))
        
        ttk.Button(btn_frame, 
                  text="Manage Parties", 
                  command=self.main_app.open_party_form,
                  style='Primary.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Transport Management", 
                  command=self.main_app.open_transport_form,
                  style='Modern.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Agent Management", 
                  command=self.main_app.open_agent_form,
                  style='Modern.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Import Data", 
                  command=self.main_app.open_data_import_form,
                  style='Warning.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="About", 
                  command=self.main_app.show_about,
                  style='Success.TButton').pack(pady=2, fill='x')
    
    def create_documents_card(self, parent):
        """Create documents card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        title = ttk.Label(card, text="📄 Documents", style='Title.TLabel')
        title.pack(pady=(10, 5))
        
        desc = ttk.Label(card, 
                        text="Credit notes, debit notes, and document management",
                        font=('Arial', 9),
                        background=self.colors['card'],
                        foreground=self.colors['muted'],
                        wraplength=200)
        desc.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(card)
        btn_frame.pack(pady=(0, 10))
        
        ttk.Button(btn_frame, 
                  text="Credit Notes", 
                  command=self.main_app.open_credit_notes_form,
                  style='Primary.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Debit Notes", 
                  command=self.main_app.open_debit_notes_form,
                  style='Primary.TButton').pack(pady=2, fill='x')
        
        ttk.Button(btn_frame, 
                  text="Trial Balance", 
                  command=self.main_app.show_trial_balance,
                  style='Success.TButton').pack(pady=2, fill='x')
