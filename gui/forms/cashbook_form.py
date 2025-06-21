"""
Cash Book Entry form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries

class CashBookForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Cash Book Entry")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_cash_entries()
        
    def setup_form(self):
        """Setup the cash book form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create cash entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Cash Book Entry", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Date:").grid(row=0, column=0, sticky='w', pady=2)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(entry_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Voucher No:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.vouch_no_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.vouch_no_var, width=15).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Particulars:").grid(row=1, column=0, sticky='w', pady=2)
        self.particulars_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.particulars_var, width=40).grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Party:").grid(row=2, column=0, sticky='w', pady=2)
        self.party_var = tk.StringVar()
        self.party_combo = ttk.Combobox(entry_frame, textvariable=self.party_var, width=30)
        self.party_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Type:").grid(row=3, column=0, sticky='w', pady=2)
        self.amount_type_var = tk.StringVar(value='Debit')
        ttk.Radiobutton(entry_frame, text="Debit (Receipt)", variable=self.amount_type_var, value='Debit').grid(row=3, column=1, sticky='w', pady=2)
        ttk.Radiobutton(entry_frame, text="Credit (Payment)", variable=self.amount_type_var, value='Credit').grid(row=3, column=2, sticky='w', pady=2)
        
        ttk.Label(entry_frame, text="Amount:").grid(row=4, column=0, sticky='w', pady=2)
        self.amount_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.amount_var, width=15).grid(row=4, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Balance:").grid(row=4, column=2, sticky='w', pady=2, padx=(20, 0))
        self.balance_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.balance_var, width=15, state='readonly').grid(row=4, column=3, padx=5, pady=2)
        
        self.load_parties()
        
    def create_list_section(self, parent):
        """Create cash entries list section"""
        list_frame = ttk.LabelFrame(parent, text="Cash Book Entries", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Date', 'Voucher No', 'Particulars', 'Party', 'Debit', 'Credit', 'Balance')
        self.cash_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.cash_tree.heading(col, text=col)
            if col in ['Debit', 'Credit', 'Balance']:
                self.cash_tree.column(col, width=100)
            elif col == 'Particulars':
                self.cash_tree.column(col, width=200)
            else:
                self.cash_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.cash_tree.yview)
        self.cash_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cash_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Entry", 
                  command=self.save_entry, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_form, 
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Print", 
                  command=self.print_cashbook, 
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
            
    def load_cash_entries(self):
        """Load cash book entries"""
        try:
            for item in self.cash_tree.get_children():
                self.cash_tree.delete(item)
            
            entries = self.queries.get_all_cashbook_entries()
            
            for entry in entries:
                debit = f"₹{entry['dr_amt']:.2f}" if entry['dr_amt'] > 0 else ""
                credit = f"₹{entry['cr_amt']:.2f}" if entry['cr_amt'] > 0 else ""
                balance = f"₹{entry['balance']:.2f}"
                party_name = entry.get('party_nm', '') or ''
                
                self.cash_tree.insert('', 'end', values=(
                    entry['vouch_date'],
                    entry['vouch_no'] or '',
                    entry['particulars'] or '',
                    party_name,
                    debit,
                    credit,
                    balance
                ))
                
            self.main_app.update_status(f"Loaded {len(entries)} cash book entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cash entries: {e}")
            
    def save_entry(self):
        """Save cash book entry"""
        try:
            if not self.particulars_var.get().strip():
                messagebox.showerror("Error", "Please enter particulars")
                return
            
            if not self.amount_var.get().strip():
                messagebox.showerror("Error", "Please enter amount")
                return
            
            try:
                amount = float(self.amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
            
            try:
                from datetime import datetime
                datetime.strptime(self.date_var.get(), '%d/%m/%Y')
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid date (DD/MM/YYYY)")
                return
            party_code = ''
            if self.party_var.get():
                party_code = self.party_var.get().split(' - ')[0]
            
            entry_data = {
                'vouch_date': datetime.strptime(self.date_var.get(), '%d/%m/%Y').date(),
                'vouch_no': self.vouch_no_var.get(),
                'particulars': self.particulars_var.get(),
                'dr_amt': amount if self.amount_type_var.get() == 'Debit' else 0,
                'cr_amt': amount if self.amount_type_var.get() == 'Credit' else 0,
                'balance': float(self.balance_var.get() or 0),
                'party_cd': party_code
            }
            
            if self.queries.save_cashbook_entry(entry_data):
                messagebox.showinfo("Success", "Cash book entry saved successfully")
                self.clear_form()
                self.load_cash_entries()
            else:
                messagebox.showerror("Error", "Failed to save cash book entry")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.date_var.set(datetime.now().strftime('%d/%m/%Y'))
        self.vouch_no_var.set('')
        self.particulars_var.set('')
        self.party_var.set('')
        self.amount_var.set('')
        self.balance_var.set('')
        self.amount_type_var.set('Debit')
        
    def print_cashbook(self):
        """Print cash book"""
        try:
            print_window = tk.Toplevel(self.window)
            print_window.title("Cash Book - Print Preview")
            print_window.geometry("800x600")
            
            report_text = self.generate_cashbook_report()
            
            text_widget = tk.Text(print_window, font=('Courier', 10))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
            button_frame = ttk.Frame(print_window)
            button_frame.pack(fill='x', pady=5)
            
            ttk.Button(button_frame, text="Export to PDF", 
                      command=self.export_to_pdf, 
                      style='Warning.TButton').pack(side='right', padx=5)
            
            ttk.Button(button_frame, text="Export to Excel", 
                      command=self.export_to_excel, 
                      style='Success.TButton').pack(side='right', padx=5)
            
            ttk.Button(button_frame, text="Export to CSV", 
                      command=self.export_to_csv, 
                      style='Modern.TButton').pack(side='right', padx=5)
            
            ttk.Button(button_frame, text="Close", 
                      command=print_window.destroy).pack(side='right', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print: {e}")
    
    def generate_cashbook_report(self):
        """Generate cash book report text"""
        lines = []
        lines.append("=" * 80)
        lines.append("CASH BOOK REPORT".center(80))
        lines.append("=" * 80)
        lines.append(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("-" * 80)
        lines.append(f"{'Date':<12} {'Voucher':<10} {'Particulars':<25} {'Party':<15} {'Debit':<12} {'Credit':<12}")
        lines.append("-" * 80)
        
        for child in self.cash_tree.get_children():
            values = self.cash_tree.item(child)['values']
            lines.append(f"{values[0]:<12} {values[1]:<10} {values[2]:<25} {values[3]:<15} {values[4]:<12} {values[5]:<12}")
        
        lines.append("=" * 80)
        return '\n'.join(lines)
    
    def export_to_pdf(self):
        """Export cash book to PDF"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Voucher No', 'Particulars', 'Party', 'Debit', 'Credit']
            data = []
            
            for child in self.cash_tree.get_children():
                values = self.cash_tree.item(child)['values']
                data.append(values[:6])
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            title = "Cash Book Report"
            ExportUtils.export_to_pdf(data, headers, title, "cashbook_report")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def export_to_excel(self):
        """Export cash book to Excel"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Voucher No', 'Particulars', 'Party', 'Debit', 'Credit']
            data = []
            
            for child in self.cash_tree.get_children():
                values = self.cash_tree.item(child)['values']
                data.append(values[:6])
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_excel(data, headers, "cashbook_report", "Cash Book")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {e}")
    
    def export_to_csv(self):
        """Export cash book to CSV"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Voucher No', 'Particulars', 'Party', 'Debit', 'Credit']
            data = []
            
            for child in self.cash_tree.get_children():
                values = self.cash_tree.item(child)['values']
                data.append(values[:6])
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_csv(data, headers, "cashbook_report")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
