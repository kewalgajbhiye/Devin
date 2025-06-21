"""
Stock report form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries

class StockReportForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Stock Report")
        self.window.geometry("900x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_stock_data()
        
    def setup_form(self):
        """Setup the stock report form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_header_section(main_frame)
        self.create_report_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_header_section(self, parent):
        """Create header section"""
        header_frame = ttk.LabelFrame(parent, text="Stock Report Options", padding=10)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="As on Date:").grid(row=0, column=0, sticky='w', pady=2)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(header_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(header_frame, text="Category:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.category_var = tk.StringVar(value='ALL')
        category_combo = ttk.Combobox(header_frame, textvariable=self.category_var, width=15)
        category_combo['values'] = ('ALL', 'VEGETABLES', 'FRUITS', 'GRAINS', 'SPICES', 'OTHER')
        category_combo.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Button(header_frame, text="Refresh Report", 
                  command=self.load_stock_data, 
                  style='Primary.TButton').grid(row=0, column=4, padx=20, pady=2)
        
    def create_report_section(self, parent):
        """Create report section"""
        report_frame = ttk.LabelFrame(parent, text="Current Stock", padding=10)
        report_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Item Code', 'Item Name', 'Unit', 'Current Stock', 'Rate', 'Stock Value')
        self.stock_tree = ttk.Treeview(report_frame, columns=columns, show='headings')
        
        for col in columns:
            self.stock_tree.heading(col, text=col)
            if col == 'Item Name':
                self.stock_tree.column(col, width=200)
            elif col in ['Current Stock', 'Stock Value']:
                self.stock_tree.column(col, width=120)
            else:
                self.stock_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(report_frame, orient='vertical', command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stock_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        summary_frame = ttk.Frame(report_frame)
        summary_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(summary_frame, text="Total Items:", font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        self.total_items_var = tk.StringVar(value='0')
        ttk.Label(summary_frame, textvariable=self.total_items_var).pack(side='left')
        
        ttk.Label(summary_frame, text="Total Stock Value:", font=('Arial', 10, 'bold')).pack(side='right', padx=5)
        self.total_value_var = tk.StringVar(value='₹0.00')
        ttk.Label(summary_frame, textvariable=self.total_value_var, 
                 foreground=self.settings.colors['primary']).pack(side='right')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_report, 
                  style='Success.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to CSV", 
                  command=self.export_to_csv, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Print Report", 
                  command=self.print_report, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_stock_data(self):
        """Load stock data"""
        try:
            for item in self.stock_tree.get_children():
                self.stock_tree.delete(item)
            
            category = self.category_var.get()
            if category == 'ALL':
                items = self.queries.get_all_items()
            else:
                items = [item for item in self.queries.get_all_items() 
                        if item.get('category', '').upper() == category.upper()]
            
            total_value = 0.0
            
            for item in items:
                purchases = self.queries.get_item_purchases(item['it_cd'])
                sales = self.queries.get_item_sales(item['it_cd'])
                
                total_purchased = sum(p.get('qty', 0) for p in purchases)
                total_sold = sum(s.get('qty', 0) for s in sales)
                current_stock = total_purchased - total_sold
                
                rate = item.get('rate', 0)
                stock_value = current_stock * rate
                total_value += stock_value
                
                self.stock_tree.insert('', 'end', values=(
                    item['it_cd'],
                    item['it_nm'],
                    item.get('unit', 'KG'),
                    f"{current_stock:.2f}",
                    f"₹{rate:.2f}",
                    f"₹{stock_value:.2f}"
                ))
            
            self.total_items_var.set(str(len(items)))
            self.total_value_var.set(f"₹{total_value:.2f}")
            
            self.main_app.update_status(f"Stock report loaded: {len(items)} items")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stock data: {e}")
            
    def export_report(self):
        """Export report to Excel"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Item Code', 'Item Name', 'Unit', 'Current Stock', 'Rate', 'Stock Value']
            data = []
            
            for child in self.stock_tree.get_children():
                values = self.stock_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_excel(data, headers, "stock_report", "Stock Report")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {e}")
            
    def print_report(self):
        """Print report"""
        try:
            print_window = tk.Toplevel(self.window)
            print_window.title("Stock Report - Print Preview")
            print_window.geometry("800x600")
            
            report_text = self.generate_report_text()
            
            text_widget = tk.Text(print_window, font=('Courier', 10))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
            ttk.Button(print_window, text="Close", 
                      command=print_window.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print report: {e}")
            
    def generate_report_text(self):
        """Generate report text for printing"""
        lines = []
        lines.append("=" * 80)
        lines.append("STOCK REPORT".center(80))
        lines.append("=" * 80)
        lines.append(f"Date: {self.date_var.get()}")
        lines.append(f"Category: {self.category_var.get()}")
        lines.append("-" * 80)
        lines.append(f"{'Code':<10} {'Name':<25} {'Unit':<8} {'Stock':<12} {'Rate':<12} {'Value':<12}")
        lines.append("-" * 80)
        
        for child in self.stock_tree.get_children():
            values = self.stock_tree.item(child)['values']
            lines.append(f"{values[0]:<10} {values[1]:<25} {values[2]:<8} {values[3]:<12} {values[4]:<12} {values[5]:<12}")
        
        lines.append("-" * 80)
        lines.append(f"Total Items: {self.total_items_var.get()}")
        lines.append(f"Total Value: {self.total_value_var.get()}")
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    def export_to_csv(self):
        """Export report to CSV"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Item Code', 'Item Name', 'Unit', 'Current Stock', 'Rate', 'Stock Value']
            data = []
            
            for child in self.stock_tree.get_children():
                values = self.stock_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_csv(data, headers, "stock_report")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
