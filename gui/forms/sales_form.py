"""
Sales entry form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries
from business.sales import SalesManager

class SalesEntryForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        self.sales_manager = SalesManager(db_manager)
        self.edit_mode = False
        self.original_bill_no = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Sales Entry")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.items_list = []
        self.total_amount = 0.0
        
        self.setup_form()
        
        self.window.update_idletasks()
        self.window.after(100, self.load_initial_data)
        
    def setup_form(self):
        """Setup the sales entry form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_header_section(main_frame)
        self.create_items_section(main_frame)
        self.create_expenses_section(main_frame)
        self.create_crate_section(main_frame)
        self.create_buttons_section(main_frame)
        
        self.load_next_bill_number()
        
    def create_header_section(self, parent):
        """Create header section with bill details"""
        header_frame = ttk.LabelFrame(parent, text="Sales Details", padding=10)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="Bill No:").grid(row=0, column=0, sticky='w', pady=2)
        self.bill_no_var = tk.StringVar()
        ttk.Entry(header_frame, textvariable=self.bill_no_var, width=15, state='readonly').grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(header_frame, text="Date:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(header_frame, textvariable=self.date_var, width=15).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(header_frame, text="Party:").grid(row=0, column=4, sticky='w', pady=2, padx=(20, 0))
        self.party_var = tk.StringVar()
        self.party_combo = ttk.Combobox(header_frame, textvariable=self.party_var, width=30)
        self.party_combo.grid(row=0, column=5, padx=5, pady=2)
        self.party_combo.bind('<KeyRelease>', self.on_party_search)
        
        ttk.Label(header_frame, text="Transport:").grid(row=1, column=0, sticky='w', pady=2)
        self.transport_var = tk.StringVar()
        ttk.Entry(header_frame, textvariable=self.transport_var, width=20).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(header_frame, text="Vehicle No:").grid(row=1, column=2, sticky='w', pady=2, padx=(20, 0))
        self.vehicle_var = tk.StringVar()
        ttk.Entry(header_frame, textvariable=self.vehicle_var, width=15).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(header_frame, text="Remarks:").grid(row=1, column=4, sticky='w', pady=2, padx=(20, 0))
        self.remarks_var = tk.StringVar()
        ttk.Entry(header_frame, textvariable=self.remarks_var, width=30).grid(row=1, column=5, padx=5, pady=2)
        
    def create_items_section(self, parent):
        """Create items section"""
        items_frame = ttk.LabelFrame(parent, text="Items", padding=10)
        items_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        entry_frame = ttk.Frame(items_frame)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Item:").grid(row=0, column=0, sticky='w', pady=2)
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(entry_frame, textvariable=self.item_var, width=25)
        self.item_combo.grid(row=0, column=1, padx=5, pady=2)
        self.item_combo.bind('<KeyRelease>', self.on_item_search)
        
        ttk.Label(entry_frame, text="Quantity:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.qty_var = tk.StringVar(value='1')
        ttk.Entry(entry_frame, textvariable=self.qty_var, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Rate:").grid(row=0, column=4, sticky='w', pady=2, padx=(20, 0))
        self.rate_var = tk.StringVar(value='0')
        ttk.Entry(entry_frame, textvariable=self.rate_var, width=10).grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Button(entry_frame, text="Add Item", 
                  command=self.add_item, 
                  style='Success.TButton').grid(row=0, column=6, padx=10, pady=2)
        
        columns = ('Item Code', 'Item Name', 'Quantity', 'Rate', 'Amount')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.items_tree.heading(col, text=col)
            if col == 'Item Name':
                self.items_tree.column(col, width=200)
            else:
                self.items_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(items_frame, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.items_tree.bind('<Delete>', self.delete_item)
        
        total_frame = ttk.Frame(items_frame)
        total_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(total_frame, text="Total Amount:", font=('Arial', 12, 'bold')).pack(side='right', padx=5)
        self.total_var = tk.StringVar(value='₹0.00')
        ttk.Label(total_frame, textvariable=self.total_var, 
                 font=('Arial', 12, 'bold'), 
                 foreground=self.settings.colors['primary']).pack(side='right')
    
    def create_expenses_section(self, parent):
        """Create expenses section"""
        expenses_frame = ttk.LabelFrame(parent, text="Expenses", padding=10)
        expenses_frame.pack(fill='x', pady=(0, 10))
        
        left_exp = ttk.Frame(expenses_frame)
        left_exp.pack(side='left', fill='x', expand=True)
        
        right_exp = ttk.Frame(expenses_frame)
        right_exp.pack(side='right', fill='x', expand=True, padx=(20, 0))
        
        ttk.Label(left_exp, text="Tapaal:").grid(row=0, column=0, sticky='w', pady=2)
        self.exp1_var = tk.StringVar(value='0')
        ttk.Entry(left_exp, textvariable=self.exp1_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(left_exp, text="Bhada:").grid(row=1, column=0, sticky='w', pady=2)
        self.exp2_var = tk.StringVar(value='0')
        ttk.Entry(left_exp, textvariable=self.exp2_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(left_exp, text="Rail Freight:").grid(row=2, column=0, sticky='w', pady=2)
        self.exp3_var = tk.StringVar(value='0')
        ttk.Entry(left_exp, textvariable=self.exp3_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(right_exp, text="Hamali:").grid(row=0, column=0, sticky='w', pady=2)
        self.exp4_var = tk.StringVar(value='0')
        ttk.Entry(right_exp, textvariable=self.exp4_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(right_exp, text="Others:").grid(row=1, column=0, sticky='w', pady=2)
        self.exp5_var = tk.StringVar(value='0')
        ttk.Entry(right_exp, textvariable=self.exp5_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(right_exp, text="Advance:").grid(row=2, column=0, sticky='w', pady=2)
        self.cash_var = tk.StringVar(value='0')
        ttk.Entry(right_exp, textvariable=self.cash_var, width=10).grid(row=2, column=1, padx=5, pady=2)
    
    def create_crate_section(self, parent):
        """Create crate handling section"""
        crate_frame = ttk.LabelFrame(parent, text="Crate Management", padding=10)
        crate_frame.pack(fill='x', pady=(0, 10))
        
        left_crate = ttk.Frame(crate_frame)
        left_crate.pack(side='left', fill='x', expand=True)
        
        right_crate = ttk.Frame(crate_frame)
        right_crate.pack(side='right', fill='x', expand=True, padx=(20, 0))
        
        ttk.Label(left_crate, text="Total Crates:").grid(row=0, column=0, sticky='w', pady=2)
        self.total_crates_var = tk.StringVar(value='0')
        ttk.Entry(left_crate, textvariable=self.total_crates_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(left_crate, text="Crate Type:").grid(row=1, column=0, sticky='w', pady=2)
        self.crate_type_var = tk.StringVar()
        crate_types = ['Jute Bags - 50 KG', 'Plastic Crates - 20 KG', 'Gunny Bags - 40 KG', 
                      'Cardboard Boxes - 10 KG', 'Mesh Bags - 25 KG']
        self.crate_combo = ttk.Combobox(left_crate, textvariable=self.crate_type_var, 
                                       values=crate_types, width=20)
        self.crate_combo.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(right_crate, text="Crate Bhada:").grid(row=0, column=0, sticky='w', pady=2)
        self.crate_bhada_var = tk.StringVar(value='0')
        ttk.Entry(right_crate, textvariable=self.crate_bhada_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(right_crate, text="Crate Rate:").grid(row=1, column=0, sticky='w', pady=2)
        self.crate_rate_var = tk.StringVar(value='0')
        ttk.Entry(right_crate, textvariable=self.crate_rate_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(crate_frame, text="Calculate Crate Charges", 
                  command=self.calculate_crate_charges,
                  style='Success.TButton').pack(side='right', padx=5)
    
    def calculate_crate_charges(self):
        """Calculate crate charges based on quantity and rate"""
        try:
            total_crates = float(self.total_crates_var.get() or 0)
            crate_rate = float(self.crate_rate_var.get() or 0)
            
            crate_bhada = total_crates * crate_rate
            self.crate_bhada_var.set(f"{crate_bhada:.2f}")
            
            current_exp2 = float(self.exp2_var.get() or 0)
            total_bhada = current_exp2 + crate_bhada
            self.exp2_var.set(f"{total_bhada:.2f}")
            
            messagebox.showinfo("Success", f"Crate charges calculated: ₹{crate_bhada:.2f}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for crate calculation")
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Sale", 
                  command=self.save_sale, 
                  style='Primary.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_form, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_next_bill_number(self):
        """Load next bill number"""
        try:
            next_bill = self.db_manager.get_next_bill_number('sales')
            self.bill_no_var.set(str(next_bill))
        except Exception as e:
            print(f"Error loading next bill number: {e}")
            self.bill_no_var.set('1')
            
    def load_initial_data(self):
        """Load initial data for dropdowns"""
        try:
            print(f"🔍 SalesForm.load_initial_data() called")
            
            parties = self.queries.get_all_parties()
            print(f"👥 Retrieved {len(parties)} parties for dropdown")
            
            if parties:
                party_list = [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
                self.party_combo['values'] = party_list
                print(f"  Set party dropdown values: {party_list[:3]}...")
            
            items = self.queries.get_all_items()
            print(f"📦 Retrieved {len(items)} items for dropdown")
            
            if items:
                item_list = [f"{i['it_cd']} - {i['it_nm']}" for i in items]
                self.item_combo['values'] = item_list
                print(f"  Set item dropdown values: {item_list[:3]}...")
            
            print(f"✅ Sales form dropdowns loaded successfully")
            
        except Exception as e:
            print(f"❌ Error in SalesForm.load_initial_data(): {e}")
            import traceback
            traceback.print_exc()
            
    def on_party_search(self, event):
        """Handle party search"""
        search_term = self.party_var.get()
        if len(search_term) >= 2:
            parties = self.queries.search_parties(search_term)
            party_list = [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
            self.party_combo['values'] = party_list
            
    def on_item_search(self, event):
        """Handle item search"""
        search_term = self.item_var.get()
        if len(search_term) >= 2:
            items = self.queries.search_items(search_term)
            item_list = [f"{i['it_cd']} - {i['it_nm']}" for i in items]
            self.item_combo['values'] = item_list
            
    def add_item(self):
        """Add item to the list"""
        try:
            if not self.item_var.get():
                messagebox.showerror("Error", "Please select an item")
                return
                
            item_text = self.item_var.get()
            if ' - ' not in item_text:
                messagebox.showerror("Error", "Please select a valid item from the dropdown")
                return
                
            item_code = item_text.split(' - ')[0]
            item_name = item_text.split(' - ')[1]
            
            try:
                quantity = float(self.qty_var.get())
                rate = float(self.rate_var.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid quantity and rate")
                return
                
            amount = quantity * rate
            
            self.items_tree.insert('', 'end', values=(
                item_code, item_name, quantity, f"₹{rate:.2f}", f"₹{amount:.2f}"
            ))
            
            self.items_list.append({
                'item_code': item_code,
                'item_name': item_name,
                'quantity': quantity,
                'rate': rate,
                'amount': amount
            })
            
            self.update_total()
            
            self.item_var.set('')
            self.qty_var.set('1')
            self.rate_var.set('0')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {e}")
            
    def delete_item(self, event):
        """Delete selected item"""
        selection = self.items_tree.selection()
        if selection:
            item_index = self.items_tree.index(selection[0])
            self.items_tree.delete(selection[0])
            del self.items_list[item_index]
            self.update_total()
            
    def update_total(self):
        """Update total amount"""
        self.total_amount = sum(item['amount'] for item in self.items_list)
        self.total_var.set(f"₹{self.total_amount:.2f}")
        
    def save_sale(self):
        """Save sales entry"""
        try:
            if not self.party_var.get():
                messagebox.showerror("Error", "Please select a party")
                return
                
            if not self.items_list:
                messagebox.showerror("Error", "Please add at least one item")
                return
                
            party_code = self.party_var.get().split(' - ')[0]
            
            sale_data = {
                'bill_no': int(self.bill_no_var.get()),
                'bill_dt': self.date_var.get(),
                'party_cd': party_code,
                'transport': self.transport_var.get(),
                'vehicle_no': self.vehicle_var.get(),
                'remarks': self.remarks_var.get(),
                'total_amount': self.total_amount,
                'exp1': float(self.exp1_var.get() or 0),
                'exp2': float(self.exp2_var.get() or 0),
                'exp3': float(self.exp3_var.get() or 0),
                'exp4': float(self.exp4_var.get() or 0),
                'exp5': float(self.exp5_var.get() or 0),
                'cash': float(self.cash_var.get() or 0),
                'total_crates': int(self.total_crates_var.get() or 0),
                'crate_type': self.crate_type_var.get(),
                'crate_bhada': float(self.crate_bhada_var.get() or 0),
                'items': self.items_list
            }
            
            success, message = self.sales_manager.create_sales_entry(sale_data, self.items_list)
            if success:
                messagebox.showinfo("Success", f"Sale {sale_data['bill_no']} saved successfully")
                self.main_app.update_status(f"Sale {sale_data['bill_no']} saved successfully")
                self.clear_form()
                self.load_next_bill_number()
            else:
                messagebox.showerror("Error", f"Failed to save sale: {message}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sale: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.party_var.set('')
        self.transport_var.set('')
        self.vehicle_var.set('')
        self.remarks_var.set('')
        self.item_var.set('')
        self.qty_var.set('1')
        self.rate_var.set('0')
        self.exp1_var.set('0')
        self.exp2_var.set('0')
        self.exp3_var.set('0')
        self.exp4_var.set('0')
        self.exp5_var.set('0')
        self.cash_var.set('0')
        self.total_crates_var.set('0')
        self.crate_type_var.set('')
        self.crate_bhada_var.set('0')
        self.crate_rate_var.set('0')
        
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        self.items_list.clear()
        self.edit_mode = False
        self.original_bill_no = None
        self.window.title("Sales Entry")
        self.update_total()
    
    def load_sale_for_edit(self, bill_no, sale_data):
        """Load existing sale data for editing"""
        try:
            self.edit_mode = True
            self.original_bill_no = bill_no
            
            if sale_data:
                first_record = sale_data[0]
                self.party_var.set(f"{first_record.get('party_cd', '')} - {first_record.get('party_nm', '')}")
                self.transport_var.set(first_record.get('transport', ''))
                self.vehicle_var.set(first_record.get('vehicle', ''))
                self.remarks_var.set(first_record.get('remarks', ''))
                
                self.exp1_var.set(str(first_record.get('exp1', 0)))
                self.exp2_var.set(str(first_record.get('exp2', 0)))
                self.exp3_var.set(str(first_record.get('exp3', 0)))
                self.exp4_var.set(str(first_record.get('exp4', 0)))
                self.exp5_var.set(str(first_record.get('exp5', 0)))
                self.cash_var.set(str(first_record.get('cash', 0)))
                
                self.items_list = []
                for item in sale_data:
                    self.items_list.append({
                        'it_cd': item.get('it_cd', ''),
                        'it_nm': item.get('it_nm', ''),
                        'qty': item.get('qty', 0),
                        'rate': item.get('rate', 0),
                        'sal_amt': item.get('sal_amt', 0)
                    })
                
                for item in self.items_tree.get_children():
                    self.items_tree.delete(item)
                
                for item in self.items_list:
                    self.items_tree.insert('', 'end', values=(
                        item.get('it_nm', ''),
                        f"{item.get('qty', 0):.2f}",
                        f"₹{item.get('rate', 0):.2f}",
                        f"₹{item.get('sal_amt', 0):.2f}"
                    ))
                
                self.update_total()
                self.window.title(f"Edit Sale - Bill #{bill_no}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sale data: {e}")
