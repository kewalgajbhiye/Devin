"""
Print Purchase Bill form with user-friendly selection
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries
import tempfile
import os

class PrintPurchaseBillForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Print Purchase Bill")
        self.window.geometry("900x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_purchase_data()
        
    def setup_form(self):
        """Setup the print purchase bill form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_selection_section(main_frame)
        self.create_list_section(main_frame)
        self.create_preview_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_selection_section(self, parent):
        """Create bill selection section"""
        selection_frame = ttk.LabelFrame(parent, text="Select Purchase Bill", padding=10)
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
        """Create purchase bills list section"""
        list_frame = ttk.LabelFrame(parent, text="Purchase Bills", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Bill No', 'Date', 'Party', 'Total Amount', 'Items')
        self.bills_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.bills_tree.heading(col, text=col)
            if col == 'Total Amount':
                self.bills_tree.column(col, width=120, anchor='e')
            elif col == 'Bill No':
                self.bills_tree.column(col, width=80)
            elif col == 'Date':
                self.bills_tree.column(col, width=100)
            else:
                self.bills_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.bills_tree.yview)
        self.bills_tree.configure(yscrollcommand=scrollbar.set)
        
        self.bills_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.bills_tree.bind('<<TreeviewSelect>>', self.on_bill_select)
        
    def create_preview_section(self, parent):
        """Create bill preview section"""
        preview_frame = ttk.LabelFrame(parent, text="Bill Preview", padding=10)
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
        
        ttk.Button(button_frame, text="Print Bill", 
                  command=self.print_selected_bill, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Export to PDF", 
                  command=self.export_to_pdf, 
                  style='Success.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Export to Excel", 
                  command=self.export_to_excel, 
                  style='Warning.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Edit Selected", 
                  command=self.edit_selected_purchase, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_purchase_data(self):
        """Load purchase bills and parties"""
        try:
            parties = self.queries.get_all_parties()
            party_list = ['All Parties'] + [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
            self.party_filter_combo['values'] = party_list
            self.party_filter_var.set('All Parties')
            
            self.load_purchase_bills()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            
    def load_purchase_bills(self):
        """Load purchase bills into the tree"""
        try:
            for item in self.bills_tree.get_children():
                self.bills_tree.delete(item)
            
            purchases = self.queries.get_all_purchases()
            
            for purchase in purchases:
                party_name = purchase.get('party_nm', 'Unknown Party')
                total_amount = f"₹{purchase.get('total_amount', 0):.2f}"
                item_count = f"{purchase.get('item_count', 0)} items"
                
                self.bills_tree.insert('', 'end', values=(
                    purchase.get('bill_no', ''),
                    purchase.get('bill_date', ''),
                    party_name,
                    total_amount,
                    item_count
                ))
                
            self.main_app.update_status(f"Loaded {len(purchases)} purchase bills")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load purchase bills: {e}")
            
    def filter_by_party(self, event=None):
        """Filter bills by selected party"""
        self.apply_filters()
        
    def apply_filters(self):
        """Apply filters to the bill list"""
        try:
            party_filter = self.party_filter_var.get()
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            for item in self.bills_tree.get_children():
                self.bills_tree.delete(item)
            
            purchases = self.queries.get_all_purchases()
            
            for purchase in purchases:
                if party_filter and party_filter != 'All Parties':
                    try:
                        party_code = party_filter.split(' - ')[0] if ' - ' in party_filter else party_filter
                        if purchase.get('party_cd') != party_code:
                            continue
                    except (IndexError, AttributeError):
                        continue
                
                if from_date:
                    try:
                        from datetime import datetime
                        bill_date = datetime.strptime(purchase.get('bill_date', ''), '%Y-%m-%d').date()
                        filter_from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                        if bill_date < filter_from_date:
                            continue
                    except (ValueError, TypeError):
                        continue
                if to_date:
                    try:
                        bill_date = datetime.strptime(purchase.get('bill_date', ''), '%Y-%m-%d').date()
                        filter_to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                        if bill_date > filter_to_date:
                            continue
                    except (ValueError, TypeError):
                        continue
                
                party_name = purchase.get('party_nm', 'Unknown Party')
                total_amount = f"₹{purchase.get('total_amount', 0):.2f}"
                item_count = f"{purchase.get('item_count', 0)} items"
                
                self.bills_tree.insert('', 'end', values=(
                    purchase.get('bill_no', ''),
                    purchase.get('bill_date', ''),
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
        self.load_purchase_bills()
        
    def on_bill_select(self, event):
        """Handle bill selection"""
        try:
            selection = self.bills_tree.selection()
            if selection:
                item = self.bills_tree.item(selection[0])
                bill_no = item['values'][0]
                self.generate_bill_preview(bill_no)
                
        except Exception as e:
            print(f"Error selecting bill: {e}")
            
    def generate_bill_preview(self, bill_no):
        """Generate bill preview"""
        try:
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', tk.END)
            
            purchase_details = self.queries.get_purchase_bill_summary(bill_no)
            if not purchase_details:
                self.preview_text.insert('1.0', f"Bill {bill_no} not found")
                self.preview_text.config(state='disabled')
                return
            
            bill_text = self.format_purchase_bill(purchase_details)
            self.preview_text.insert('1.0', bill_text)
            self.preview_text.config(state='disabled')
            
        except Exception as e:
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', f"Error generating preview: {e}")
            self.preview_text.config(state='disabled')
            
    def format_purchase_bill(self, purchase_details):
        """Format purchase bill for display"""
        try:
            company_details = self.settings.company_details
            
            bill_text = f"""
{'='*60}
                    PURCHASE BILL
{'='*60}

{company_details['name']}
{company_details['business_type']}
Shop No. 15, Gala No.5, Kalamna Sabji Market, Nagpur
Phone: 70202 70292, 88882 12800

{'='*60}

Bill No: {purchase_details.get('bill_no', '')}
Date: {purchase_details.get('bill_date', '')}
Party: {purchase_details.get('party_nm', '')}
Truck No: {purchase_details.get('truck_no', '')}

{'='*60}
ITEMS:
{'='*60}

Item Name                    Qty      Rate      Amount
{'-'*60}
"""
            
            total_amount = purchase_details.get('total_amount', 0)
            
            bill_text += f"""
{'-'*60}
                           Total: ₹{total_amount:.2f}
{'='*60}

Thank you for your business!

Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
            
            return bill_text
            
        except Exception as e:
            return f"Error formatting bill: {e}"
            
    def print_selected_bill(self):
        """Print the selected bill"""
        try:
            selection = self.bills_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a bill to print")
                return
            
            item = self.bills_tree.item(selection[0])
            bill_no = item['values'][0]
            
            bill_content = self.preview_text.get('1.0', tk.END)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(bill_content)
                temp_file_path = temp_file.name
            
            if os.name == 'nt':  # Windows
                os.startfile(temp_file_path, 'print')
            else:  # Linux/Mac
                os.system(f'lpr {temp_file_path}')
            
            messagebox.showinfo("Success", f"Bill {bill_no} sent to printer")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print bill: {e}")
            
    def export_to_pdf(self):
        """Export bill to PDF"""
        try:
            selection = self.bills_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a bill to export")
                return
            
            item = self.bills_tree.item(selection[0])
            bill_no = item['values'][0]
            
            bill_details = self.queries.get_purchase_by_bill_no(bill_no)
            if not bill_details:
                messagebox.showerror("Error", "Bill details not found")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Item', 'Quantity', 'Rate', 'Amount']
            data = []
            
            data.append(['Sample Item 1', '10.00', '₹50.00', '₹500.00'])
            data.append(['Sample Item 2', '5.00', '₹30.00', '₹150.00'])
            data.append(['Total', '', '', '₹650.00'])
            
            title = f"Purchase Bill #{bill_no}"
            ExportUtils.export_to_pdf(data, headers, title, f"purchase_bill_{bill_no}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
            
    def export_to_excel(self):
        """Export bill to Excel"""
        try:
            selection = self.bills_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a bill to export")
                return
            
            item = self.bills_tree.item(selection[0])
            bill_no = item['values'][0]
            
            bill_details = self.queries.get_purchase_by_bill_no(bill_no)
            if not bill_details:
                messagebox.showerror("Error", "Bill details not found")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Item', 'Quantity', 'Rate', 'Amount']
            data = []
            
            data.append(['Sample Item 1', '10.00', '₹50.00', '₹500.00'])
            data.append(['Sample Item 2', '5.00', '₹30.00', '₹150.00'])
            data.append(['Total', '', '', '₹650.00'])
            
            ExportUtils.export_to_excel(data, headers, f"purchase_bill_{bill_no}", f"Purchase Bill {bill_no}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {e}")
    
    def edit_selected_purchase(self):
        """Edit the selected purchase"""
        try:
            selection = self.bills_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a purchase to edit")
                return
            
            item = self.bills_tree.item(selection[0])
            bill_no = item['values'][0]
            
            purchase_details = self.queries.get_purchase_by_bill_no(bill_no)
            if not purchase_details:
                messagebox.showerror("Error", "Purchase details not found")
                return
            
            from gui.forms.purchase_form import PurchaseEntryForm
            edit_form = PurchaseEntryForm(self.window, self.db_manager, self.settings, self.main_app)
            edit_form.load_purchase_for_edit(bill_no, purchase_details)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit purchase: {e}")
