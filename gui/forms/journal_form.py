"""
Journal Entry form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries

class JournalForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Journal Entry")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_journal_entries()
        
    def setup_form(self):
        """Setup the journal form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create journal entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Journal Entry", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Date:").grid(row=0, column=0, sticky='w', pady=2)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(entry_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Voucher No:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.vouch_no_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.vouch_no_var, width=15).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Reference No:").grid(row=0, column=4, sticky='w', pady=2, padx=(20, 0))
        self.ref_no_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.ref_no_var, width=15).grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Party:").grid(row=1, column=0, sticky='w', pady=2)
        self.party_var = tk.StringVar()
        self.party_combo = ttk.Combobox(entry_frame, textvariable=self.party_var, width=30)
        self.party_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Particulars:").grid(row=2, column=0, sticky='w', pady=2)
        self.particulars_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.particulars_var, width=40).grid(row=2, column=1, columnspan=5, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Type:").grid(row=3, column=0, sticky='w', pady=2)
        self.amount_type_var = tk.StringVar(value='Debit')
        ttk.Radiobutton(entry_frame, text="Debit", variable=self.amount_type_var, value='Debit').grid(row=3, column=1, sticky='w', pady=2)
        ttk.Radiobutton(entry_frame, text="Credit", variable=self.amount_type_var, value='Credit').grid(row=3, column=2, sticky='w', pady=2)
        
        ttk.Label(entry_frame, text="Amount:").grid(row=4, column=0, sticky='w', pady=2)
        self.amount_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.amount_var, width=15).grid(row=4, column=1, padx=5, pady=2)
        
        self.load_parties()
        
    def create_list_section(self, parent):
        """Create journal entries list section"""
        list_frame = ttk.LabelFrame(parent, text="Journal Entries", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Date', 'Voucher No', 'Party', 'Particulars', 'Debit', 'Credit', 'Ref No')
        self.journal_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.journal_tree.heading(col, text=col)
            if col in ['Debit', 'Credit']:
                self.journal_tree.column(col, width=100)
            elif col == 'Particulars':
                self.journal_tree.column(col, width=200)
            else:
                self.journal_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.journal_tree.yview)
        self.journal_tree.configure(yscrollcommand=scrollbar.set)
        
        self.journal_tree.pack(side='left', fill='both', expand=True)
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
                  command=self.print_journal, 
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
            
    def load_journal_entries(self):
        """Load journal entries"""
        try:
            for item in self.journal_tree.get_children():
                self.journal_tree.delete(item)
            
            entries = self.queries.get_all_journal_entries()
            
            for entry in entries:
                debit = f"₹{entry['dr_amt']:.2f}" if entry['dr_amt'] > 0 else ""
                credit = f"₹{entry['cr_amt']:.2f}" if entry['cr_amt'] > 0 else ""
                party_name = entry.get('party_nm', '') or ''
                
                self.journal_tree.insert('', 'end', values=(
                    entry['vouch_date'],
                    entry['vouch_no'] or '',
                    party_name,
                    entry['particulars'] or '',
                    debit,
                    credit,
                    entry['ref_no'] or ''
                ))
                
            self.main_app.update_status(f"Loaded {len(entries)} journal entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load journal entries: {e}")
            
    def save_entry(self):
        """Save journal entry"""
        try:
            if not self.particulars_var.get().strip():
                messagebox.showerror("Error", "Please enter particulars")
                return
            
            if not self.amount_var.get().strip():
                messagebox.showerror("Error", "Please enter amount")
                return
            
            if not self.party_var.get():
                messagebox.showerror("Error", "Please select a party")
                return
            
            amount = float(self.amount_var.get())
            party_code = self.party_var.get().split(' - ')[0]
            
            entry_data = {
                'vouch_date': datetime.strptime(self.date_var.get(), '%d/%m/%Y').date(),
                'vouch_no': self.vouch_no_var.get(),
                'party_cd': party_code,
                'particulars': self.particulars_var.get(),
                'dr_amt': amount if self.amount_type_var.get() == 'Debit' else 0,
                'cr_amt': amount if self.amount_type_var.get() == 'Credit' else 0,
                'ref_no': self.ref_no_var.get()
            }
            
            if self.queries.save_journal_entry(entry_data):
                messagebox.showinfo("Success", "Journal entry saved successfully")
                self.clear_form()
                self.load_journal_entries()
            else:
                messagebox.showerror("Error", "Failed to save journal entry")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.date_var.set(datetime.now().strftime('%d/%m/%Y'))
        self.vouch_no_var.set('')
        self.ref_no_var.set('')
        self.party_var.set('')
        self.particulars_var.set('')
        self.amount_var.set('')
        self.amount_type_var.set('Debit')
        
    def print_journal(self):
        """Print journal"""
        try:
            print_window = tk.Toplevel(self.window)
            print_window.title("Journal - Print Preview")
            print_window.geometry("800x600")
            
            report_text = self.generate_journal_report()
            
            text_widget = tk.Text(print_window, font=('Courier', 10))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
            button_frame = ttk.Frame(print_window)
            button_frame.pack(pady=5)
            
            ttk.Button(button_frame, text="Export to PDF", 
                      command=lambda: self.export_journal_to_pdf()).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Export to Excel", 
                      command=lambda: self.export_journal_to_excel()).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Export to CSV", 
                      command=lambda: self.export_journal_to_csv()).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Close", 
                      command=print_window.destroy).pack(side='left', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print journal: {e}")
    
    def generate_journal_report(self):
        """Generate journal report text"""
        lines = []
        lines.append("=" * 80)
        lines.append("JOURNAL ENTRIES REPORT".center(80))
        lines.append("=" * 80)
        lines.append(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("-" * 80)
        lines.append(f"{'Date':<12} {'Voucher':<10} {'Party':<20} {'Particulars':<25} {'Debit':<12} {'Credit':<12}")
        lines.append("-" * 80)
        
        for child in self.journal_tree.get_children():
            values = self.journal_tree.item(child)['values']
            lines.append(f"{values[0]:<12} {values[1]:<10} {values[2]:<20} {values[3]:<25} {values[4]:<12} {values[5]:<12}")
        
        lines.append("=" * 80)
        return '\n'.join(lines)
    
    def export_journal_to_pdf(self):
        """Export journal to PDF"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Voucher No', 'Party', 'Particulars', 'Debit', 'Credit', 'Ref No']
            data = []
            
            for child in self.journal_tree.get_children():
                values = self.journal_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            title = "Journal Entries Report"
            ExportUtils.export_to_pdf(data, headers, title, "journal_entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def export_journal_to_excel(self):
        """Export journal to Excel"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Voucher No', 'Party', 'Particulars', 'Debit', 'Credit', 'Ref No']
            data = []
            
            for child in self.journal_tree.get_children():
                values = self.journal_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_excel(data, headers, "journal_entries", "Journal Entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {e}")
    
    def export_journal_to_csv(self):
        """Export journal to CSV"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Voucher No', 'Party', 'Particulars', 'Debit', 'Credit', 'Ref No']
            data = []
            
            for child in self.journal_tree.get_children():
                values = self.journal_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_csv(data, headers, "journal_entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
