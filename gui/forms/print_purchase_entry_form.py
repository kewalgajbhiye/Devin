"""
Print Purchase Entry form with user-friendly bill selection
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from database.queries import DatabaseQueries
from business.export_utils import ExportUtils
import tempfile
import os
import subprocess
import platform

class PrintPurchaseEntryForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Print Purchase Entry")
        self.window.geometry("800x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_initial_data()
        
    def setup_form(self):
        """Setup the print purchase entry form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_filter_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_filter_section(self, parent):
        """Create filter section"""
        filter_frame = ttk.LabelFrame(parent, text="Filter Purchase Entries", padding=10)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        left_frame = ttk.Frame(filter_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        right_frame = ttk.Frame(filter_frame)
        right_frame.pack(side='right', fill='x', expand=True, padx=(20, 0))
        
        ttk.Label(left_frame, text="From Date:").grid(row=0, column=0, sticky='w', pady=2)
        self.from_date_var = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
        ttk.Entry(left_frame, textvariable=self.from_date_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(left_frame, text="To Date:").grid(row=1, column=0, sticky='w', pady=2)
        self.to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        ttk.Entry(left_frame, textvariable=self.to_date_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(right_frame, text="Party:").grid(row=0, column=0, sticky='w', pady=2)
        self.party_var = tk.StringVar()
        self.party_combo = ttk.Combobox(right_frame, textvariable=self.party_var, width=25)
        self.party_combo.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(right_frame, text="Bill No:").grid(row=1, column=0, sticky='w', pady=2)
        self.bill_no_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.bill_no_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(filter_frame, text="Search", 
                  command=self.search_purchases,
                  style='Primary.TButton').pack(side='right', padx=5)
        
    def create_list_section(self, parent):
        """Create purchase list section"""
        list_frame = ttk.LabelFrame(parent, text="Purchase Entries", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Bill No', 'Date', 'Party', 'Amount', 'Items')
        self.purchase_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.purchase_tree.heading(col, text=col)
            if col == 'Party':
                self.purchase_tree.column(col, width=200)
            elif col == 'Items':
                self.purchase_tree.column(col, width=150)
            else:
                self.purchase_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.purchase_tree.yview)
        self.purchase_tree.configure(yscrollcommand=scrollbar.set)
        
        self.purchase_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Print Selected", 
                  command=self.print_selected,
                  style='Primary.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Print Preview", 
                  command=self.print_preview,
                  style='Success.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Export to PDF", 
                  command=self.export_pdf,
                  style='Modern.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy,
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_initial_data(self):
        """Load initial data"""
        try:
            parties = self.queries.get_all_parties()
            if parties:
                party_list = ['All Parties'] + [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
                self.party_combo['values'] = party_list
                self.party_combo.set('All Parties')
            
            self.search_purchases()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            
    def search_purchases(self):
        """Search and display purchases"""
        try:
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            party_filter = self.party_var.get()
            bill_no_filter = self.bill_no_var.get()
            
            for item in self.purchase_tree.get_children():
                self.purchase_tree.delete(item)
            
            purchases = self.queries.get_purchases_by_date_range(from_date, to_date)
            
            for purchase in purchases:
                if party_filter and party_filter != 'All Parties':
                    party_code = party_filter.split(' - ')[0]
                    if purchase.get('party_cd') != party_code:
                        continue
                
                if bill_no_filter and str(purchase.get('bill_no', '')) != bill_no_filter:
                    continue
                
                party_name = purchase.get('party_nm', 'Unknown')
                amount = f"₹{purchase.get('sal_amt', 0):.2f}"
                items = purchase.get('it_nm', 'N/A')
                
                self.purchase_tree.insert('', 'end', values=(
                    purchase.get('bill_no', ''),
                    purchase.get('bill_date', ''),
                    party_name,
                    amount,
                    items
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search purchases: {e}")
            
    def get_selected_purchase(self):
        """Get selected purchase entry"""
        selection = self.purchase_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a purchase entry to print")
            return None
            
        item = self.purchase_tree.item(selection[0])
        bill_no = item['values'][0]
        
        try:
            purchase = self.queries.get_purchase_by_bill_no(bill_no)
            return purchase
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get purchase details: {e}")
            return None
            
    def print_preview(self):
        """Show print preview"""
        purchase = self.get_selected_purchase()
        if not purchase:
            return
            
        preview_window = tk.Toplevel(self.window)
        preview_window.title(f"Print Preview - Purchase Bill {purchase.get('bill_no', '')}")
        preview_window.geometry("600x800")
        
        text_widget = tk.Text(preview_window, wrap='word', font=('Courier', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        content = self.generate_purchase_bill_text(purchase)
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')
        
        button_frame = ttk.Frame(preview_window)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Print", 
                  command=lambda: self.print_document(content),
                  style='Primary.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=preview_window.destroy,
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def print_selected(self):
        """Print selected purchase entry"""
        purchase = self.get_selected_purchase()
        if not purchase:
            return
            
        content = self.generate_purchase_bill_text(purchase)
        self.print_document(content)
        
    def print_document(self, content):
        """Print document using system print dialog"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            system = platform.system()
            if system == "Windows":
                os.startfile(temp_file, "print")
            elif system == "Darwin":
                subprocess.run(["lpr", temp_file])
            else:
                subprocess.run(["lpr", temp_file])
                
            messagebox.showinfo("Success", "Document sent to printer")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print: {e}")
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass
                
    def export_pdf(self):
        """Export selected purchase to PDF"""
        purchase = self.get_selected_purchase()
        if not purchase:
            return
            
        content = self.generate_purchase_bill_text(purchase)
        lines = content.split('\n')
        data = [line.split() for line in lines if line.strip()]
        
        ExportUtils.export_to_pdf(
            data, 
            ['Purchase Bill Details'], 
            f"Purchase Bill {purchase.get('bill_no', '')}", 
            f"purchase_bill_{purchase.get('bill_no', '')}"
        )
        
    def generate_purchase_bill_text(self, purchase):
        """Generate purchase bill text for printing"""
        lines = []
        lines.append("=" * 60)
        lines.append("PURCHASE BILL")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Bill No    : {purchase.get('bill_no', '')}")
        lines.append(f"Date       : {purchase.get('bill_date', '')}")
        lines.append(f"Party      : {purchase.get('party_nm', 'N/A')}")
        lines.append(f"Order No   : {purchase.get('order_no', '')}")
        lines.append(f"LR No      : {purchase.get('lr_no', '')}")
        lines.append(f"Transport  : {purchase.get('trans_cd', '')}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("ITEM DETAILS")
        lines.append("-" * 60)
        lines.append(f"Item       : {purchase.get('it_nm', 'N/A')}")
        lines.append(f"Quantity   : {purchase.get('qty', 0)}")
        lines.append(f"Rate       : ₹{purchase.get('rate', 0):.2f}")
        lines.append(f"Amount     : ₹{purchase.get('sal_amt', 0):.2f}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("EXPENSES")
        lines.append("-" * 60)
        lines.append(f"Tapaal     : ₹{purchase.get('exp1', 0):.2f}")
        lines.append(f"Bhada      : ₹{purchase.get('exp2', 0):.2f}")
        lines.append(f"Rail Freight: ₹{purchase.get('exp3', 0):.2f}")
        lines.append(f"Hamali     : ₹{purchase.get('exp4', 0):.2f}")
        lines.append(f"Others     : ₹{purchase.get('exp5', 0):.2f}")
        lines.append(f"Advance    : ₹{purchase.get('cash', 0):.2f}")
        lines.append("")
        total_expenses = sum([
            purchase.get('exp1', 0), purchase.get('exp2', 0), 
            purchase.get('exp3', 0), purchase.get('exp4', 0), 
            purchase.get('exp5', 0), purchase.get('cash', 0)
        ])
        grand_total = purchase.get('sal_amt', 0) + total_expenses
        lines.append(f"Total Expenses: ₹{total_expenses:.2f}")
        lines.append(f"Grand Total   : ₹{grand_total:.2f}")
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
