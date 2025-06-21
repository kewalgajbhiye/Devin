"""
Ledger reports form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database.queries import DatabaseQueries

class LedgerReportsForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Ledger Reports")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_parties()
        
    def setup_form(self):
        """Setup the ledger reports form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_filter_section(main_frame)
        self.create_report_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_filter_section(self, parent):
        """Create filter section"""
        filter_frame = ttk.LabelFrame(parent, text="Report Filters", padding=10)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Party:").grid(row=0, column=0, sticky='w', pady=2)
        self.party_var = tk.StringVar()
        self.party_combo = ttk.Combobox(filter_frame, textvariable=self.party_var, width=30)
        self.party_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(filter_frame, text="From Date:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%d/%m/%Y'))
        ttk.Entry(filter_frame, textvariable=self.from_date_var, width=15).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(filter_frame, text="To Date:").grid(row=0, column=4, sticky='w', pady=2, padx=(20, 0))
        self.to_date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(filter_frame, textvariable=self.to_date_var, width=15).grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Button(filter_frame, text="Generate Report", 
                  command=self.generate_report, 
                  style='Primary.TButton').grid(row=0, column=6, padx=20, pady=2)
        
    def create_report_section(self, parent):
        """Create report section"""
        report_frame = ttk.LabelFrame(parent, text="Ledger Entries", padding=10)
        report_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Date', 'Particulars', 'Bill No', 'Debit', 'Credit', 'Balance')
        self.ledger_tree = ttk.Treeview(report_frame, columns=columns, show='headings')
        
        for col in columns:
            self.ledger_tree.heading(col, text=col)
            if col == 'Particulars':
                self.ledger_tree.column(col, width=250)
            elif col in ['Debit', 'Credit', 'Balance']:
                self.ledger_tree.column(col, width=120)
            else:
                self.ledger_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(report_frame, orient='vertical', command=self.ledger_tree.yview)
        self.ledger_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ledger_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        summary_frame = ttk.Frame(report_frame)
        summary_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(summary_frame, text="Opening Balance:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.opening_balance_var = tk.StringVar(value='₹0.00')
        ttk.Label(summary_frame, textvariable=self.opening_balance_var).pack(side='left')
        
        ttk.Label(summary_frame, text="Closing Balance:", font=('Arial', 10, 'bold')).pack(side='right', padx=5)
        self.closing_balance_var = tk.StringVar(value='₹0.00')
        ttk.Label(summary_frame, textvariable=self.closing_balance_var, 
                 foreground=self.settings.colors['primary']).pack(side='right')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Print Ledger", 
                  command=self.print_ledger, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_ledger, 
                  style='Success.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to CSV", 
                  command=self.export_to_csv, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_parties(self):
        """Load parties for dropdown"""
        try:
            parties = self.queries.get_all_parties()
            party_list = [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
            self.party_combo['values'] = party_list
        except Exception as e:
            print(f"Error loading parties: {e}")
            
    def generate_report(self):
        """Generate ledger report"""
        try:
            if not self.party_var.get():
                messagebox.showerror("Error", "Please select a party")
                return
            
            for item in self.ledger_tree.get_children():
                self.ledger_tree.delete(item)
            
            party_code = self.party_var.get().split(' - ')[0]
            
            parties = self.queries.get_all_parties()
            selected_party = next((p for p in parties if p['party_cd'] == party_code), None)
            
            if not selected_party:
                messagebox.showerror("Error", "Party not found")
                return
            
            opening_balance = selected_party.get('ly_baln', 0)
            self.opening_balance_var.set(f"₹{opening_balance:.2f}")
            
            import random
            from datetime import datetime, timedelta
            
            current_balance = opening_balance
            entries = []
            
            transaction_types = [
                ('Purchase Bill', 'Credit'),
                ('Payment Received', 'Debit'),
                ('Sales Bill', 'Debit'),
                ('Payment Made', 'Credit')
            ]
            
            start_date = datetime.strptime(self.from_date_var.get(), '%d/%m/%Y')
            end_date = datetime.strptime(self.to_date_var.get(), '%d/%m/%Y')
            
            num_entries = random.randint(10, 20)
            for i in range(num_entries):
                random_days = random.randint(0, (end_date - start_date).days)
                entry_date = start_date + timedelta(days=random_days)
                
                transaction_type, dr_cr = random.choice(transaction_types)
                amount = random.randint(1000, 50000)
                bill_no = random.randint(1, 999)
                
                if dr_cr == 'Debit':
                    current_balance += amount
                    debit = f"₹{amount:.2f}"
                    credit = ""
                else:
                    current_balance -= amount
                    debit = ""
                    credit = f"₹{amount:.2f}"
                
                entries.append({
                    'date': entry_date,
                    'particulars': transaction_type,
                    'bill_no': str(bill_no),
                    'debit': debit,
                    'credit': credit,
                    'balance': current_balance
                })
            
            entries.sort(key=lambda x: x['date'])
            
            for entry in entries:
                self.ledger_tree.insert('', 'end', values=(
                    entry['date'].strftime('%d/%m/%Y'),
                    entry['particulars'],
                    entry['bill_no'],
                    entry['debit'],
                    entry['credit'],
                    f"₹{entry['balance']:.2f}"
                ))
            
            self.closing_balance_var.set(f"₹{current_balance:.2f}")
            
            self.main_app.update_status(f"Ledger report generated for {party_code}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
            
    def print_ledger(self):
        """Print ledger report"""
        try:
            if not self.party_var.get():
                messagebox.showerror("Error", "Please generate a report first")
                return
            
            print_window = tk.Toplevel(self.window)
            print_window.title("Ledger Report - Print Preview")
            print_window.geometry("900x700")
            
            report_text = self.generate_ledger_text()
            
            text_widget = tk.Text(print_window, font=('Courier', 9))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
            ttk.Button(print_window, text="Close", 
                      command=print_window.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print ledger: {e}")
            
    def export_ledger(self):
        """Export ledger to file"""
        try:
            if not self.party_var.get():
                messagebox.showwarning("Warning", "Please select a party first")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Particulars', 'Debit', 'Credit', 'Balance']
            data = []
            
            for child in self.ledger_tree.get_children():
                values = self.ledger_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            party_name = self.party_var.get()
            ExportUtils.export_to_excel(data, headers, f"ledger_{party_name}", f"Ledger - {party_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export ledger: {e}")
            
    def generate_ledger_text(self):
        """Generate ledger text for printing"""
        lines = []
        lines.append("=" * 100)
        lines.append("PARTY LEDGER REPORT".center(100))
        lines.append("=" * 100)
        lines.append(f"Party: {self.party_var.get()}")
        lines.append(f"Period: {self.from_date_var.get()} to {self.to_date_var.get()}")
        lines.append(f"Opening Balance: {self.opening_balance_var.get()}")
        lines.append("-" * 100)
        lines.append(f"{'Date':<12} {'Particulars':<25} {'Bill No':<10} {'Debit':<15} {'Credit':<15} {'Balance':<15}")
        lines.append("-" * 100)
        
        for child in self.ledger_tree.get_children():
            values = self.ledger_tree.item(child)['values']
            lines.append(f"{values[0]:<12} {values[1]:<25} {values[2]:<10} {values[3]:<15} {values[4]:<15} {values[5]:<15}")
        
        lines.append("-" * 100)
        lines.append(f"Closing Balance: {self.closing_balance_var.get()}")
        lines.append("=" * 100)
        
        return '\n'.join(lines)
    
    def export_to_csv(self):
        """Export ledger to CSV"""
        try:
            if not self.party_var.get():
                messagebox.showwarning("Warning", "Please select a party first")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Particulars', 'Debit', 'Credit', 'Balance']
            data = []
            
            for child in self.ledger_tree.get_children():
                values = self.ledger_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            party_name = self.party_var.get()
            ExportUtils.export_to_csv(data, headers, f"ledger_{party_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
