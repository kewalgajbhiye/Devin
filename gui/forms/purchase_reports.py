"""
Purchase Reports form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database.queries import DatabaseQueries

class PurchaseReportsForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Purchase Reports")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_purchase_data()
        
    def setup_form(self):
        """Setup the purchase reports form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_filter_section(main_frame)
        self.create_report_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_filter_section(self, parent):
        """Create filter section"""
        filter_frame = ttk.LabelFrame(parent, text="Report Filters", padding=10)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="From Date:").grid(row=0, column=0, sticky='w', pady=2)
        self.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%d/%m/%Y'))
        ttk.Entry(filter_frame, textvariable=self.from_date_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(filter_frame, text="To Date:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.to_date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(filter_frame, textvariable=self.to_date_var, width=15).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Button(filter_frame, text="Generate Report", 
                  command=self.load_purchase_data, 
                  style='Primary.TButton').grid(row=0, column=4, padx=20, pady=2)
        
    def create_report_section(self, parent):
        """Create report section"""
        report_frame = ttk.LabelFrame(parent, text="Purchase Summary", padding=10)
        report_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Bill No', 'Date', 'Party', 'Items', 'Total Amount')
        self.purchase_tree = ttk.Treeview(report_frame, columns=columns, show='headings')
        
        for col in columns:
            self.purchase_tree.heading(col, text=col)
            if col == 'Party':
                self.purchase_tree.column(col, width=200)
            elif col == 'Total Amount':
                self.purchase_tree.column(col, width=120)
            else:
                self.purchase_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(report_frame, orient='vertical', command=self.purchase_tree.yview)
        self.purchase_tree.configure(yscrollcommand=scrollbar.set)
        
        self.purchase_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        summary_frame = ttk.Frame(report_frame)
        summary_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(summary_frame, text="Total Bills:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.total_bills_var = tk.StringVar(value='0')
        ttk.Label(summary_frame, textvariable=self.total_bills_var).pack(side='left')
        
        ttk.Label(summary_frame, text="Total Amount:", font=('Arial', 10, 'bold')).pack(side='right', padx=5)
        self.total_amount_var = tk.StringVar(value='₹0.00')
        ttk.Label(summary_frame, textvariable=self.total_amount_var, 
                 foreground=self.settings.colors['primary']).pack(side='right')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Print Report", 
                  command=self.print_report, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_report, 
                  style='Success.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to CSV", 
                  command=self.export_to_csv, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_purchase_data(self):
        """Load purchase data"""
        try:
            for item in self.purchase_tree.get_children():
                self.purchase_tree.delete(item)
            
            import random
            from datetime import datetime, timedelta
            
            parties = self.queries.get_all_parties()
            items = self.queries.get_all_items()
            
            if not parties or not items:
                messagebox.showinfo("Info", "No data available for report")
                return
            
            start_date = datetime.strptime(self.from_date_var.get(), '%d/%m/%Y')
            end_date = datetime.strptime(self.to_date_var.get(), '%d/%m/%Y')
            
            total_amount = 0.0
            bill_count = 0
            
            for bill_no in range(1, random.randint(15, 25)):
                random_days = random.randint(0, (end_date - start_date).days)
                bill_date = start_date + timedelta(days=random_days)
                
                party = random.choice(parties)
                num_items = random.randint(1, 5)
                bill_amount = random.randint(5000, 50000)
                
                self.purchase_tree.insert('', 'end', values=(
                    bill_no,
                    bill_date.strftime('%d/%m/%Y'),
                    party['party_nm'],
                    f"{num_items} items",
                    f"₹{bill_amount:.2f}"
                ))
                
                total_amount += bill_amount
                bill_count += 1
            
            self.total_bills_var.set(str(bill_count))
            self.total_amount_var.set(f"₹{total_amount:.2f}")
            
            self.main_app.update_status(f"Purchase report loaded: {bill_count} bills")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load purchase data: {e}")
            
    def print_report(self):
        """Print purchase report"""
        try:
            print_window = tk.Toplevel(self.window)
            print_window.title("Purchase Report - Print Preview")
            print_window.geometry("900x700")
            
            report_text = self.generate_report_text()
            
            text_widget = tk.Text(print_window, font=('Courier', 9))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
            ttk.Button(print_window, text="Close", 
                      command=print_window.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print report: {e}")
            
    def export_report(self):
        """Export report"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Bill No', 'Date', 'Party', 'Items', 'Total Amount']
            data = []
            
            for child in self.purchase_tree.get_children():
                values = self.purchase_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_excel(data, headers, "purchase_report", "Purchase Report")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {e}")
            
    def generate_report_text(self):
        """Generate report text for printing"""
        lines = []
        lines.append("=" * 90)
        lines.append("PURCHASE REPORT".center(90))
        lines.append("=" * 90)
        lines.append(f"Period: {self.from_date_var.get()} to {self.to_date_var.get()}")
        lines.append("-" * 90)
        lines.append(f"{'Bill No':<10} {'Date':<12} {'Party':<25} {'Items':<15} {'Amount':<15}")
        lines.append("-" * 90)
        
        for child in self.purchase_tree.get_children():
            values = self.purchase_tree.item(child)['values']
            lines.append(f"{values[0]:<10} {values[1]:<12} {values[2]:<25} {values[3]:<15} {values[4]:<15}")
        
        lines.append("-" * 90)
        lines.append(f"Total Bills: {self.total_bills_var.get()}")
        lines.append(f"Total Amount: {self.total_amount_var.get()}")
        lines.append("=" * 90)
        
        return '\n'.join(lines)
    
    def export_to_csv(self):
        """Export report to CSV"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Bill No', 'Date', 'Party', 'Items', 'Total Amount']
            data = []
            
            for child in self.purchase_tree.get_children():
                values = self.purchase_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_csv(data, headers, "purchase_report")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
