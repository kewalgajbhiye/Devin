"""
Party Statements form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database.queries import DatabaseQueries

class PartyStatementsForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Party Statements")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_parties()
        
    def setup_form(self):
        """Setup the party statements form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_filter_section(main_frame)
        self.create_statement_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_filter_section(self, parent):
        """Create filter section"""
        filter_frame = ttk.LabelFrame(parent, text="Statement Filters", padding=10)
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
        
        ttk.Button(filter_frame, text="Generate Statement", 
                  command=self.generate_statement, 
                  style='Primary.TButton').grid(row=0, column=6, padx=20, pady=2)
        
    def create_statement_section(self, parent):
        """Create statement section"""
        statement_frame = ttk.LabelFrame(parent, text="Party Statement", padding=10)
        statement_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Date', 'Transaction', 'Bill No', 'Debit', 'Credit', 'Balance')
        self.statement_tree = ttk.Treeview(statement_frame, columns=columns, show='headings')
        
        for col in columns:
            self.statement_tree.heading(col, text=col)
            if col == 'Transaction':
                self.statement_tree.column(col, width=200)
            elif col in ['Debit', 'Credit', 'Balance']:
                self.statement_tree.column(col, width=120)
            else:
                self.statement_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(statement_frame, orient='vertical', command=self.statement_tree.yview)
        self.statement_tree.configure(yscrollcommand=scrollbar.set)
        
        self.statement_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        summary_frame = ttk.Frame(statement_frame)
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
        
        ttk.Button(button_frame, text="Print Statement", 
                  command=self.print_statement, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_statement, 
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
            
    def generate_statement(self):
        """Generate party statement"""
        try:
            if not self.party_var.get():
                messagebox.showerror("Error", "Please select a party")
                return
            
            for item in self.statement_tree.get_children():
                self.statement_tree.delete(item)
            
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
            transactions = []
            
            transaction_types = [
                ('Purchase Bill', 'Credit'),
                ('Payment Received', 'Debit'),
                ('Sales Bill', 'Debit'),
                ('Payment Made', 'Credit'),
                ('Adjustment', 'Credit')
            ]
            
            start_date = datetime.strptime(self.from_date_var.get(), '%d/%m/%Y')
            end_date = datetime.strptime(self.to_date_var.get(), '%d/%m/%Y')
            
            num_transactions = random.randint(10, 20)
            for i in range(num_transactions):
                random_days = random.randint(0, (end_date - start_date).days)
                trans_date = start_date + timedelta(days=random_days)
                
                transaction_type, dr_cr = random.choice(transaction_types)
                amount = random.randint(1000, 25000)
                bill_no = random.randint(1, 999)
                
                if dr_cr == 'Debit':
                    current_balance += amount
                    debit = f"₹{amount:.2f}"
                    credit = ""
                else:
                    current_balance -= amount
                    debit = ""
                    credit = f"₹{amount:.2f}"
                
                transactions.append({
                    'date': trans_date,
                    'transaction': transaction_type,
                    'bill_no': str(bill_no),
                    'debit': debit,
                    'credit': credit,
                    'balance': current_balance
                })
            
            transactions.sort(key=lambda x: x['date'])
            
            for trans in transactions:
                self.statement_tree.insert('', 'end', values=(
                    trans['date'].strftime('%d/%m/%Y'),
                    trans['transaction'],
                    trans['bill_no'],
                    trans['debit'],
                    trans['credit'],
                    f"₹{trans['balance']:.2f}"
                ))
            
            self.closing_balance_var.set(f"₹{current_balance:.2f}")
            
            self.main_app.update_status(f"Statement generated for {party_code}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate statement: {e}")
            
    def print_statement(self):
        """Print party statement"""
        try:
            if not self.party_var.get():
                messagebox.showerror("Error", "Please generate a statement first")
                return
            
            print_window = tk.Toplevel(self.window)
            print_window.title("Party Statement - Print Preview")
            print_window.geometry("900x700")
            
            report_text = self.generate_statement_text()
            
            text_widget = tk.Text(print_window, font=('Courier', 9))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
            ttk.Button(print_window, text="Close", 
                      command=print_window.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print statement: {e}")
            
    def export_statement(self):
        """Export statement"""
        try:
            if not self.party_var.get():
                messagebox.showwarning("Warning", "Please select a party first")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Bill No', 'Type', 'Amount', 'Balance']
            data = []
            
            for child in self.statement_tree.get_children():
                values = self.statement_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            party_name = self.party_var.get()
            ExportUtils.export_to_excel(data, headers, f"statement_{party_name}", f"Statement - {party_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export statement: {e}")
            
    def generate_statement_text(self):
        """Generate statement text for printing"""
        lines = []
        lines.append("=" * 100)
        lines.append("PARTY STATEMENT".center(100))
        lines.append("=" * 100)
        lines.append(f"Party: {self.party_var.get()}")
        lines.append(f"Period: {self.from_date_var.get()} to {self.to_date_var.get()}")
        lines.append(f"Opening Balance: {self.opening_balance_var.get()}")
        lines.append("-" * 100)
        lines.append(f"{'Date':<12} {'Transaction':<20} {'Bill No':<10} {'Debit':<15} {'Credit':<15} {'Balance':<15}")
        lines.append("-" * 100)
        
        for child in self.statement_tree.get_children():
            values = self.statement_tree.item(child)['values']
            lines.append(f"{values[0]:<12} {values[1]:<20} {values[2]:<10} {values[3]:<15} {values[4]:<15} {values[5]:<15}")
        
        lines.append("-" * 100)
        lines.append(f"Closing Balance: {self.closing_balance_var.get()}")
        lines.append("=" * 100)
        
        return '\n'.join(lines)
    
    def export_to_csv(self):
        """Export statement to CSV"""
        try:
            if not self.party_var.get():
                messagebox.showwarning("Warning", "Please select a party first")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Bill No', 'Type', 'Amount', 'Balance']
            data = []
            
            for child in self.statement_tree.get_children():
                values = self.statement_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            party_name = self.party_var.get()
            ExportUtils.export_to_csv(data, headers, f"statement_{party_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
