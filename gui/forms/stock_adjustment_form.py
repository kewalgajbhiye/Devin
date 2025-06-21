"""
Stock Adjustment form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries

class StockAdjustmentForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Stock Adjustment")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_adjustments()
        
    def setup_form(self):
        """Setup the stock adjustment form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create adjustment entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Stock Adjustment Entry", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Date:").grid(row=0, column=0, sticky='w', pady=2)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(entry_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Item:").grid(row=1, column=0, sticky='w', pady=2)
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(entry_frame, textvariable=self.item_var, width=30)
        self.item_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Adjustment Type:").grid(row=2, column=0, sticky='w', pady=2)
        self.adj_type_var = tk.StringVar(value='INCREASE')
        ttk.Radiobutton(entry_frame, text="Increase", variable=self.adj_type_var, value='INCREASE').grid(row=2, column=1, sticky='w', pady=2)
        ttk.Radiobutton(entry_frame, text="Decrease", variable=self.adj_type_var, value='DECREASE').grid(row=2, column=2, sticky='w', pady=2)
        
        ttk.Label(entry_frame, text="Quantity:").grid(row=3, column=0, sticky='w', pady=2)
        self.qty_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.qty_var, width=15).grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Reason:").grid(row=4, column=0, sticky='w', pady=2)
        self.reason_var = tk.StringVar()
        reasons = [
            'Spoilage due to weather',
            'Damage during transport',
            'Quality rejection',
            'Weight loss due to drying',
            'Counting error correction',
            'Stock taking adjustment',
            'Other'
        ]
        self.reason_combo = ttk.Combobox(entry_frame, textvariable=self.reason_var, values=reasons, width=30)
        self.reason_combo.grid(row=4, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        self.load_items()
        
    def create_list_section(self, parent):
        """Create adjustments list section"""
        list_frame = ttk.LabelFrame(parent, text="Stock Adjustments", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Date', 'Item', 'Type', 'Quantity', 'Reason')
        self.adj_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.adj_tree.heading(col, text=col)
            if col == 'Item':
                self.adj_tree.column(col, width=200)
            elif col == 'Reason':
                self.adj_tree.column(col, width=250)
            else:
                self.adj_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.adj_tree.yview)
        self.adj_tree.configure(yscrollcommand=scrollbar.set)
        
        self.adj_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Adjustment", 
                  command=self.save_adjustment, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_form, 
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Print Report", 
                  command=self.print_report, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_items(self):
        """Load items for dropdown"""
        try:
            items = self.queries.get_all_items()
            item_list = [f"{i['it_cd']} - {i['it_nm']}" for i in items]
            self.item_combo['values'] = item_list
        except Exception as e:
            print(f"Error loading items: {e}")
            
    def load_adjustments(self):
        """Load stock adjustments"""
        try:
            for item in self.adj_tree.get_children():
                self.adj_tree.delete(item)
            
            adjustments = self.queries.get_all_stock_adjustments()
            
            for adj in adjustments:
                item_name = adj.get('it_nm', '') or ''
                
                self.adj_tree.insert('', 'end', values=(
                    adj['adj_date'],
                    item_name,
                    adj['adj_type'],
                    f"{adj['adj_qty']:.2f}",
                    adj['reason'] or ''
                ))
                
            self.main_app.update_status(f"Loaded {len(adjustments)} stock adjustments")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load adjustments: {e}")
            
    def save_adjustment(self):
        """Save stock adjustment"""
        try:
            if not self.item_var.get():
                messagebox.showerror("Error", "Please select an item")
                return
            
            if not self.qty_var.get().strip():
                messagebox.showerror("Error", "Please enter quantity")
                return
            
            qty = float(self.qty_var.get())
            item_code = self.item_var.get().split(' - ')[0]
            
            adj_data = {
                'adj_date': datetime.strptime(self.date_var.get(), '%d/%m/%Y').date(),
                'it_cd': item_code,
                'adj_qty': qty,
                'adj_type': self.adj_type_var.get(),
                'reason': self.reason_var.get()
            }
            
            if self.queries.save_stock_adjustment(adj_data):
                messagebox.showinfo("Success", "Stock adjustment saved successfully")
                self.clear_form()
                self.load_adjustments()
            else:
                messagebox.showerror("Error", "Failed to save stock adjustment")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save adjustment: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.date_var.set(datetime.now().strftime('%d/%m/%Y'))
        self.item_var.set('')
        self.qty_var.set('')
        self.reason_var.set('')
        self.adj_type_var.set('INCREASE')
        
    def print_report(self):
        """Print adjustment report"""
        try:
            print_window = tk.Toplevel(self.window)
            print_window.title("Stock Adjustment Report - Print Preview")
            print_window.geometry("700x600")
            
            report_text = self.generate_adjustment_report()
            
            text_widget = tk.Text(print_window, font=('Courier', 10))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
            button_frame = ttk.Frame(print_window)
            button_frame.pack(fill='x', pady=5)
            
            ttk.Button(button_frame, text="Export to PDF", 
                      command=self.export_to_pdf).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Export to Excel", 
                      command=self.export_to_excel).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Export to CSV", 
                      command=self.export_to_csv).pack(side='left', padx=5)
            ttk.Button(button_frame, text="Close", 
                      command=print_window.destroy).pack(side='right', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print: {e}")
    
    def generate_adjustment_report(self):
        """Generate adjustment report text"""
        lines = []
        lines.append("=" * 80)
        lines.append("STOCK ADJUSTMENT REPORT".center(80))
        lines.append("=" * 80)
        lines.append(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("-" * 80)
        lines.append(f"{'Date':<12} {'Item':<25} {'Type':<10} {'Quantity':<12} {'Reason':<20}")
        lines.append("-" * 80)
        
        for child in self.adj_tree.get_children():
            values = self.adj_tree.item(child)['values']
            lines.append(f"{values[0]:<12} {values[1][:24]:<25} {values[2]:<10} {values[3]:<12} {values[4][:19]:<20}")
        
        lines.append("=" * 80)
        return '\n'.join(lines)
    
    def export_to_pdf(self):
        """Export adjustments to PDF"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Item', 'Type', 'Quantity', 'Reason']
            data = []
            
            for child in self.adj_tree.get_children():
                values = self.adj_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            title = "Stock Adjustment Report"
            ExportUtils.export_to_pdf(data, headers, title, "stock_adjustments")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def export_to_excel(self):
        """Export adjustments to Excel"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Item', 'Type', 'Quantity', 'Reason']
            data = []
            
            for child in self.adj_tree.get_children():
                values = self.adj_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_excel(data, headers, "stock_adjustments", "Stock Adjustments")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {e}")
    
    def export_to_csv(self):
        """Export adjustments to CSV"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Date', 'Item', 'Type', 'Quantity', 'Reason']
            data = []
            
            for child in self.adj_tree.get_children():
                values = self.adj_tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_csv(data, headers, "stock_adjustments")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")
