"""
Print Sales Entry form with user-friendly selection
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries
import tempfile
import os

class PrintSalesEntryForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Print Sales Entry")
        self.window.geometry("900x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_sales_data()
        
    def setup_form(self):
        """Setup the print sales entry form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_selection_section(main_frame)
        self.create_list_section(main_frame)
        self.create_preview_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_selection_section(self, parent):
        """Create sales entry selection section"""
        selection_frame = ttk.LabelFrame(parent, text="Select Sales Entry", padding=10)
        selection_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(selection_frame, text="Filter by Party:").grid(row=0, column=0, sticky='w', pady=2)
        self.party_filter_var = tk.StringVar()
        self.party_filter_combo = ttk.Combobox(selection_frame, textvariable=self.party_filter_var, width=30)
        self.party_filter_combo.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        self.party_filter_combo.bind('<<ComboboxSelected>>', self.filter_by_party)
        
        ttk.Label(selection_frame, text="From Date:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.from_date_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.from_date_var, width=12).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(selection_frame, text="To Date:").grid(row=0, column=4, sticky='w', pady=2, padx=(10, 0))
        self.to_date_var = tk.StringVar()
        ttk.Entry(selection_frame, textvariable=self.to_date_var, width=12).grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Button(selection_frame, text="Filter", 
                  command=self.apply_filters, 
                  style='Primary.TButton').grid(row=0, column=6, padx=10, pady=2)
        
        ttk.Button(selection_frame, text="Clear", 
                  command=self.clear_filters, 
                  style='Modern.TButton').grid(row=0, column=7, padx=5, pady=2)
        
        selection_frame.columnconfigure(1, weight=1)
        
    def create_list_section(self, parent):
        """Create sales entries list section"""
        list_frame = ttk.LabelFrame(parent, text="Sales Entries", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Bill No', 'Date', 'Party', 'Total Amount', 'Items')
        self.sales_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            if col == 'Total Amount':
                self.sales_tree.column(col, width=120, anchor='e')
            elif col == 'Bill No':
                self.sales_tree.column(col, width=80)
            elif col == 'Date':
                self.sales_tree.column(col, width=100)
            else:
                self.sales_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sales_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.sales_tree.bind('<<TreeviewSelect>>', self.on_sales_select)
        
    def create_preview_section(self, parent):
        """Create sales entry preview section"""
        preview_frame = ttk.LabelFrame(parent, text="Sales Entry Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.preview_text = tk.Text(preview_frame, font=('Courier', 9), height=10)
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side='left', fill='both', expand=True)
        preview_scrollbar.pack(side='right', fill='y')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Print Sales Entry", 
                  command=self.print_selected_entry, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Export to PDF", 
                  command=self.export_to_pdf, 
                  style='Success.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_to_excel, 
                  style='Warning.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_sales_data(self):
        """Load sales entries and parties"""
        try:
            parties = self.queries.get_all_parties()
            party_list = ['All Parties'] + [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
            self.party_filter_combo['values'] = party_list
            self.party_filter_var.set('All Parties')
            
            self.load_sales_entries()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            
    def load_sales_entries(self):
        """Load sales entries into the tree"""
        try:
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            
            sales = self.queries.get_all_sales()
            
            for sale in sales:
                party_name = sale.get('party_nm', 'Unknown Party')
                total_amount = f"₹{sale.get('total_amount', 0):.2f}"
                item_count = f"{sale.get('item_count', 0)} items"
                
                self.sales_tree.insert('', 'end', values=(
                    sale.get('bill_no', ''),
                    sale.get('bill_date', ''),
                    party_name,
                    total_amount,
                    item_count
                ))
                
            self.main_app.update_status(f"Loaded {len(sales)} sales entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sales entries: {e}")
            
    def filter_by_party(self, event=None):
        """Filter entries by selected party"""
        self.apply_filters()
        
    def apply_filters(self):
        """Apply filters to the entry list"""
        try:
            party_filter = self.party_filter_var.get()
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            
            sales = self.queries.get_all_sales()
            
            for sale in sales:
                if party_filter and party_filter != 'All Parties':
                    party_code = party_filter.split(' - ')[0]
                    if sale.get('party_cd') != party_code:
                        continue
                
                if from_date and sale.get('bill_date', '') < from_date:
                    continue
                if to_date and sale.get('bill_date', '') > to_date:
                    continue
                
                party_name = sale.get('party_nm', 'Unknown Party')
                total_amount = f"₹{sale.get('total_amount', 0):.2f}"
                item_count = f"{sale.get('item_count', 0)} items"
                
                self.sales_tree.insert('', 'end', values=(
                    sale.get('bill_no', ''),
                    sale.get('bill_date', ''),
                    party_name,
                    total_amount,
                    item_count
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filters: {e}")
            
    def clear_filters(self):
        """Clear all filters"""
        self.party_filter_var.set('All Parties')
        self.from_date_var.set('')
        self.to_date_var.set('')
        self.load_sales_entries()
        
    def on_sales_select(self, event):
        """Handle sales entry selection"""
        try:
            selection = self.sales_tree.selection()
            if selection:
                item = self.sales_tree.item(selection[0])
                bill_no = item['values'][0]
                self.generate_entry_preview(bill_no)
                
        except Exception as e:
            print(f"Error selecting sales entry: {e}")
            
    def generate_entry_preview(self, bill_no):
        """Generate sales entry preview"""
        try:
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', tk.END)
            
            sales_details = self.queries.get_sales_by_bill_no(bill_no)
            if not sales_details:
                self.preview_text.insert('1.0', f"Sales Entry {bill_no} not found")
                self.preview_text.config(state='disabled')
                return
            
            entry_text = self.format_sales_entry(sales_details)
            self.preview_text.insert('1.0', entry_text)
            self.preview_text.config(state='disabled')
            
        except Exception as e:
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', f"Error generating preview: {e}")
            self.preview_text.config(state='disabled')
            
    def format_sales_entry(self, sales_details):
        """Format sales entry for display"""
        try:
            company_details = self.settings.company_details
            
            entry_text = f"""
{'='*60}
                    SALES ENTRY
{'='*60}

{company_details['name']}
{company_details['business_type']}
Shop No. 15, Gala No.5, Kalamna Sabji Market, Nagpur
Phone: 70202 70292, 88882 12800

{'='*60}

Bill No: {sales_details.get('bill_no', '')}
Date: {sales_details.get('bill_date', '')}
Party: {sales_details.get('party_nm', '')}
Truck No: {sales_details.get('truck_no', '')}

{'='*60}
ITEMS:
{'='*60}

Item Name                    Qty      Rate      Amount
{'-'*60}
"""
            
            total_amount = sales_details.get('total_amount', 0)
            
            entry_text += f"""
{'-'*60}
                           Total: ₹{total_amount:.2f}
{'='*60}

Thank you for your business!

Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
            
            return entry_text
            
        except Exception as e:
            return f"Error formatting sales entry: {e}"
            
    def print_selected_entry(self):
        """Print the selected sales entry"""
        try:
            selection = self.sales_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a sales entry to print")
                return
            
            item = self.sales_tree.item(selection[0])
            bill_no = item['values'][0]
            
            entry_content = self.preview_text.get('1.0', tk.END)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(entry_content)
                temp_file_path = temp_file.name
            
            if os.name == 'nt':
                os.startfile(temp_file_path, 'print')
            else:
                os.system(f'lpr {temp_file_path}')
            
            messagebox.showinfo("Success", f"Sales Entry {bill_no} sent to printer")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print sales entry: {e}")
            
    def export_to_pdf(self):
        """Export sales entry to PDF"""
        try:
            selection = self.sales_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a sales entry to export")
                return
            
            item = self.sales_tree.item(selection[0])
            bill_no = item['values'][0]
            
            sales_details = self.queries.get_sales_by_bill_no(bill_no)
            if not sales_details:
                messagebox.showerror("Error", "Sales entry details not found")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Item', 'Quantity', 'Rate', 'Amount']
            data = []
            
            data.append(['Sample Item 1', '10.00', '₹50.00', '₹500.00'])
            data.append(['Sample Item 2', '5.00', '₹30.00', '₹150.00'])
            data.append(['Total', '', '', '₹650.00'])
            
            title = f"Sales Entry #{bill_no}"
            ExportUtils.export_to_pdf(data, headers, title, f"sales_entry_{bill_no}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
            
    def export_to_excel(self):
        """Export sales entry to Excel"""
        try:
            selection = self.sales_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a sales entry to export")
                return
            
            item = self.sales_tree.item(selection[0])
            bill_no = item['values'][0]
            
            sales_details = self.queries.get_sales_by_bill_no(bill_no)
            if not sales_details:
                messagebox.showerror("Error", "Sales entry details not found")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Item', 'Quantity', 'Rate', 'Amount']
            data = []
            
            data.append(['Sample Item 1', '10.00', '₹50.00', '₹500.00'])
            data.append(['Sample Item 2', '5.00', '₹30.00', '₹150.00'])
            data.append(['Total', '', '', '₹650.00'])
            
            ExportUtils.export_to_excel(data, headers, f"sales_entry_{bill_no}", f"Sales Entry {bill_no}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {e}")
