"""
Trial Balance Form
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from business.trial_balance import TrialBalanceManager
from database.queries import DatabaseQueries

class TrialBalanceForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        self.trial_balance_manager = TrialBalanceManager(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Trial Balance")
        self.window.geometry("1200x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_trial_balance_data()
        
    def setup_form(self):
        """Setup the trial balance form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_filter_section(main_frame)
        self.create_data_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_filter_section(self, parent):
        """Create filter section"""
        filter_frame = ttk.LabelFrame(parent, text="Filter Options", padding=10)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="From Date:").grid(row=0, column=0, sticky='w', pady=5)
        self.from_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.from_date_var, width=15).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="To Date:").grid(row=0, column=2, sticky='w', pady=5)
        self.to_date_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.to_date_var, width=15).grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Button(filter_frame, text="Apply Filter", 
                  command=self.apply_filters,
                  style='Primary.TButton').grid(row=0, column=4, padx=10, pady=5)
        
        ttk.Button(filter_frame, text="Import CSV", 
                  command=self.import_csv_data,
                  style='Warning.TButton').grid(row=0, column=5, padx=10, pady=5)
        
    def create_data_section(self, parent):
        """Create trial balance data section"""
        data_frame = ttk.LabelFrame(parent, text="Trial Balance Data", padding=10)
        data_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Party Code', 'Party Name', 'Opening Balance', 'Debit', 'Credit', 'Closing Balance', 'Date')
        self.trial_balance_tree = ttk.Treeview(data_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.trial_balance_tree.heading(col, text=col)
            if col in ['Opening Balance', 'Debit', 'Credit', 'Closing Balance']:
                self.trial_balance_tree.column(col, width=120, anchor='e')
            elif col == 'Party Code':
                self.trial_balance_tree.column(col, width=100)
            elif col == 'Date':
                self.trial_balance_tree.column(col, width=100)
            else:
                self.trial_balance_tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(data_frame, orient='vertical', command=self.trial_balance_tree.yview)
        self.trial_balance_tree.configure(yscrollcommand=scrollbar.set)
        
        self.trial_balance_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_to_excel,
                  style='Success.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Print Report", 
                  command=self.print_report,
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Refresh", 
                  command=self.load_trial_balance_data,
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy,
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_trial_balance_data(self):
        """Load trial balance data"""
        try:
            for item in self.trial_balance_tree.get_children():
                self.trial_balance_tree.delete(item)
            
            trial_balance_data = self.trial_balance_manager.get_trial_balance_report()
            
            for record in trial_balance_data:
                self.trial_balance_tree.insert('', 'end', values=(
                    record.get('party_cd', ''),
                    record.get('party_nm', ''),
                    f"₹{record.get('opening_balance', 0):.2f}",
                    f"₹{record.get('debit_amount', 0):.2f}",
                    f"₹{record.get('credit_amount', 0):.2f}",
                    f"₹{record.get('closing_balance', 0):.2f}",
                    record.get('balance_date', '')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load trial balance data: {e}")
            
    def apply_filters(self):
        """Apply date filters"""
        try:
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            for item in self.trial_balance_tree.get_children():
                self.trial_balance_tree.delete(item)
            
            trial_balance_data = self.trial_balance_manager.get_trial_balance_report(from_date, to_date)
            
            for record in trial_balance_data:
                self.trial_balance_tree.insert('', 'end', values=(
                    record.get('party_cd', ''),
                    record.get('party_nm', ''),
                    f"₹{record.get('opening_balance', 0):.2f}",
                    f"₹{record.get('debit_amount', 0):.2f}",
                    f"₹{record.get('credit_amount', 0):.2f}",
                    f"₹{record.get('closing_balance', 0):.2f}",
                    record.get('balance_date', '')
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filters: {e}")
            
    def import_csv_data(self):
        """Import trial balance data from CSV"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Trial Balance CSV file",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            imported_count = self.trial_balance_manager.import_trial_balance_data(file_path)
            
            if imported_count > 0:
                messagebox.showinfo("Success", f"Imported {imported_count} trial balance records")
                self.load_trial_balance_data()
            else:
                messagebox.showerror("Error", "No records were imported")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV data: {e}")
            
    def export_to_excel(self):
        """Export trial balance to Excel"""
        try:
            from business.export_utils import ExportUtils
            
            trial_balance_data = self.trial_balance_manager.get_trial_balance_report()
            
            if not trial_balance_data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            filename = f"trial_balance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            if ExportUtils.export_to_excel(trial_balance_data, filename, "Trial Balance"):
                messagebox.showinfo("Success", f"Trial balance exported to {filename}")
            else:
                messagebox.showerror("Error", "Failed to export trial balance")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to Excel: {e}")
            
    def print_report(self):
        """Print trial balance report"""
        try:
            trial_balance_data = self.trial_balance_manager.get_trial_balance_report()
            
            if not trial_balance_data:
                messagebox.showwarning("Warning", "No data to print")
                return
            
            report_text = self.generate_report_text(trial_balance_data)
            
            print_window = tk.Toplevel(self.window)
            print_window.title("Trial Balance Report")
            print_window.geometry("800x600")
            
            text_widget = tk.Text(print_window, font=('Courier', 10))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print report: {e}")
            
    def generate_report_text(self, trial_balance_data):
        """Generate formatted trial balance report text"""
        try:
            company_details = self.settings.company_details
            
            report_text = f"""
{'='*80}
                            TRIAL BALANCE REPORT
{'='*80}

{company_details['name']}
{company_details['business_type']}
Shop No. 15, Gala No.5, Kalamna Sabji Market, Nagpur
Phone: 70202 70292, 88882 12800

{'='*80}

Party Code    Party Name                Opening Bal    Debit        Credit       Closing Bal
{'-'*80}
"""
            
            total_opening = 0
            total_debit = 0
            total_credit = 0
            total_closing = 0
            
            for record in trial_balance_data:
                opening = record.get('opening_balance', 0)
                debit = record.get('debit_amount', 0)
                credit = record.get('credit_amount', 0)
                closing = record.get('closing_balance', 0)
                
                total_opening += opening
                total_debit += debit
                total_credit += credit
                total_closing += closing
                
                report_text += f"{record.get('party_cd', ''):<10} {record.get('party_nm', '')[:20]:<20} {opening:>12.2f} {debit:>12.2f} {credit:>12.2f} {closing:>12.2f}\n"
            
            report_text += f"""
{'-'*80}
{'TOTAL':<30} {total_opening:>12.2f} {total_debit:>12.2f} {total_credit:>12.2f} {total_closing:>12.2f}
{'='*80}

Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
            
            return report_text
            
        except Exception as e:
            return f"Error generating report: {e}"
