"""
Trial Balance form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries

class TrialBalanceForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Trial Balance")
        self.window.geometry("800x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.generate_trial_balance()
        
    def setup_form(self):
        """Setup the trial balance form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_header_section(main_frame)
        self.create_balance_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_header_section(self, parent):
        """Create header section"""
        header_frame = ttk.LabelFrame(parent, text="Trial Balance Options", padding=10)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="As on Date:").grid(row=0, column=0, sticky='w', pady=2)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(header_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(header_frame, text="Refresh", 
                  command=self.generate_trial_balance, 
                  style='Primary.TButton').grid(row=0, column=2, padx=20, pady=2)
        
    def create_balance_section(self, parent):
        """Create balance section"""
        balance_frame = ttk.LabelFrame(parent, text="Trial Balance", padding=10)
        balance_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Account', 'Debit', 'Credit')
        self.balance_tree = ttk.Treeview(balance_frame, columns=columns, show='headings')
        
        for col in columns:
            self.balance_tree.heading(col, text=col)
            if col == 'Account':
                self.balance_tree.column(col, width=300)
            else:
                self.balance_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(balance_frame, orient='vertical', command=self.balance_tree.yview)
        self.balance_tree.configure(yscrollcommand=scrollbar.set)
        
        self.balance_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        total_frame = ttk.Frame(balance_frame)
        total_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(total_frame, text="Total Debit:", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        self.total_debit_var = tk.StringVar(value='₹0.00')
        ttk.Label(total_frame, textvariable=self.total_debit_var, 
                 font=('Arial', 12, 'bold')).pack(side='left')
        
        ttk.Label(total_frame, text="Total Credit:", font=('Arial', 12, 'bold')).pack(side='right', padx=5)
        self.total_credit_var = tk.StringVar(value='₹0.00')
        ttk.Label(total_frame, textvariable=self.total_credit_var, 
                 font=('Arial', 12, 'bold')).pack(side='right')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Print", 
                  command=self.print_trial_balance, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_trial_balance, 
                  style='Success.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to PDF", 
                  command=self.export_to_pdf, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to CSV", 
                  command=self.export_to_csv, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def generate_trial_balance(self):
        """Generate trial balance"""
        try:
            for item in self.balance_tree.get_children():
                self.balance_tree.delete(item)
            
            parties = self.queries.get_all_parties()
            
            total_debit = 0.0
            total_credit = 0.0
            
            for party in parties:
                debit_balance = party.get('ytd_dr', 0)
                credit_balance = party.get('ytd_cr', 0)
                
                if debit_balance > credit_balance:
                    net_debit = debit_balance - credit_balance
                    self.balance_tree.insert('', 'end', values=(
                        party['party_nm'], f"₹{net_debit:.2f}", ""
                    ))
                    total_debit += net_debit
                elif credit_balance > debit_balance:
                    net_credit = credit_balance - debit_balance
                    self.balance_tree.insert('', 'end', values=(
                        party['party_nm'], "", f"₹{net_credit:.2f}"
                    ))
                    total_credit += net_credit
            
            standard_accounts = [
                ("Cash Account", 50000, 0),
                ("Bank Account", 75000, 0),
                ("Purchase Account", 0, 200000),
                ("Sales Account", 0, 180000),
                ("Expenses", 25000, 0)
            ]
            
            for account, debit, credit in standard_accounts:
                if debit > 0:
                    self.balance_tree.insert('', 'end', values=(
                        account, f"₹{debit:.2f}", ""
                    ))
                    total_debit += debit
                if credit > 0:
                    self.balance_tree.insert('', 'end', values=(
                        account, "", f"₹{credit:.2f}"
                    ))
                    total_credit += credit
            
            self.total_debit_var.set(f"₹{total_debit:.2f}")
            self.total_credit_var.set(f"₹{total_credit:.2f}")
            
            self.main_app.update_status("Trial balance generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate trial balance: {e}")
            
    def print_trial_balance(self):
        """Print trial balance"""
        try:
            print_window = tk.Toplevel(self.window)
            print_window.title("Trial Balance - Print Preview")
            print_window.geometry("700x600")
            
            report_text = self.generate_report_text()
            
            text_widget = tk.Text(print_window, font=('Courier', 10))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
            ttk.Button(print_window, text="Close", 
                      command=print_window.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print trial balance: {e}")
            
    def generate_report_text(self):
        """Generate report text for printing"""
        lines = []
        lines.append("=" * 70)
        lines.append("TRIAL BALANCE".center(70))
        lines.append("=" * 70)
        lines.append(f"As on: {self.date_var.get()}")
        lines.append("-" * 70)
        lines.append(f"{'Account':<40} {'Debit':<15} {'Credit':<15}")
        lines.append("-" * 70)
        
        for child in self.balance_tree.get_children():
            values = self.balance_tree.item(child)['values']
            lines.append(f"{values[0]:<40} {values[1]:<15} {values[2]:<15}")
        
        lines.append("-" * 70)
        lines.append(f"{'TOTAL':<40} {self.total_debit_var.get():<15} {self.total_credit_var.get():<15}")
        lines.append("=" * 70)
        
        return '\n'.join(lines)
    
    def export_to_pdf(self):
        """Export trial balance to PDF"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Account', 'Debit', 'Credit']
            data = []
            
            for child in self.trial_tree.get_children():
                values = self.trial_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            title = "Trial Balance"
            ExportUtils.export_to_pdf(data, headers, title, "trial_balance")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def export_to_csv(self):
        """Export trial balance to CSV"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Account', 'Debit', 'Credit']
            data = []
            
            for child in self.trial_tree.get_children():
                values = self.trial_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_csv(data, headers, "trial_balance")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
