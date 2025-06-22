"""
Purchase entry form with modern Tkinter UI
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from database.queries import DatabaseQueries
from business.purchase import PurchaseManager

class PurchaseEntryForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        self.edit_mode = False
        self.original_bill_no = None
        from business.purchase import PurchaseManager
        self.purchase_manager = PurchaseManager(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Purchase Entry")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.items_data = []
        self.setup_form()
        
    def setup_form(self):
        """Setup the purchase entry form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_header_section(main_frame)
        self.create_items_section(main_frame)
        self.create_expenses_section(main_frame)
        self.create_buttons_section(main_frame)
        
        self.load_next_bill_number()
        
        self.window.update_idletasks()
        self.window.after(100, self.load_initial_data)
        
    def create_header_section(self, parent):
        """Create header section with bill details"""
        header_frame = ttk.LabelFrame(parent, text="Purchase Details", padding=10)
        header_frame.pack(fill='x', pady=(0, 10))
        
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=(20, 0))
        
        ttk.Label(left_frame, text="Bill No:").grid(row=0, column=0, sticky='w', pady=2)
        self.bill_no_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.bill_no_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Bill Date:").grid(row=1, column=0, sticky='w', pady=2)
        self.bill_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        ttk.Entry(left_frame, textvariable=self.bill_date_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Party:").grid(row=2, column=0, sticky='w', pady=2)
        self.party_var = tk.StringVar()
        from gui.components.searchable_combobox import SearchableCombobox
        self.party_combo = SearchableCombobox.create_searchable_combobox(
            left_frame, self.party_var, [], width=25)
        self.party_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        self.party_combo.bind('<KeyRelease>', self.on_party_search)
        
        ttk.Label(right_frame, text="Order No:").grid(row=0, column=0, sticky='w', pady=2)
        self.order_no_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.order_no_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(right_frame, text="LR No:").grid(row=1, column=0, sticky='w', pady=2)
        self.lr_no_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.lr_no_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(right_frame, text="Transport:").grid(row=2, column=0, sticky='w', pady=2)
        self.trans_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.trans_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        
    def create_items_section(self, parent):
        """Create items section with treeview"""
        items_frame = ttk.LabelFrame(parent, text="Items", padding=10)
        items_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        entry_frame = ttk.Frame(items_frame)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Item:").grid(row=0, column=0, sticky='w', padx=2)
        self.item_var = tk.StringVar()
        from gui.components.searchable_combobox import SearchableCombobox
        self.item_combo = SearchableCombobox.create_searchable_combobox(
            entry_frame, self.item_var, [], width=20)
        self.item_combo.grid(row=0, column=1, padx=2)
        self.item_combo.bind('<KeyRelease>', self.on_item_search)
        
        ttk.Label(entry_frame, text="Qty:").grid(row=0, column=2, sticky='w', padx=2)
        self.qty_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.qty_var, width=10).grid(row=0, column=3, padx=2)
        
        ttk.Label(entry_frame, text="Rate:").grid(row=0, column=4, sticky='w', padx=2)
        self.rate_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.rate_var, width=10).grid(row=0, column=5, padx=2)
        
        ttk.Button(entry_frame, text="Add Item", command=self.add_item).grid(row=0, column=6, padx=10)
        
        columns = ('Item Code', 'Description', 'Qty', 'Rate', 'Amount')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.items_tree.heading(col, text=col)
            if col == 'Description':
                self.items_tree.column(col, width=200)
            else:
                self.items_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(items_frame, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.items_tree.bind('<Delete>', self.delete_item)
        
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
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text="Save Purchase", 
                  command=self.save_purchase, 
                  style='Primary.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Cancel", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_form, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
        self.total_label = ttk.Label(button_frame, text="Total: ₹0.00", 
                                   font=('Arial', 12, 'bold'))
        self.total_label.pack(side='left')
        
    def load_next_bill_number(self):
        """Load next available bill number"""
        next_bill = self.purchase_manager.get_next_bill_number()
        self.bill_no_var.set(str(next_bill))
        
    def load_initial_data(self):
        """Load initial data for dropdowns"""
        try:
            print(f"🔍 PurchaseForm.load_initial_data() called")
            print(f"🔍 Party combo exists: {hasattr(self, 'party_combo')}")
            print(f"🔍 Item combo exists: {hasattr(self, 'item_combo')}")
            
            parties = self.queries.get_all_parties()
            print(f"👥 Retrieved {len(parties)} parties for dropdown")
            
            if parties:
                party_list = [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
                self.party_combo['values'] = party_list
                from gui.components.searchable_combobox import SearchableCombobox
                SearchableCombobox.make_searchable(self.party_combo, party_list)
                print(f"  Set party dropdown values: {party_list[:3]}...")
            else:
                print("⚠️  No parties found for dropdown")
            
            items = self.queries.get_all_items()
            print(f"📦 Retrieved {len(items)} items for dropdown")
            
            if items:
                item_list = [f"{i['it_cd']} - {i['it_nm']}" for i in items]
                self.item_combo['values'] = item_list
                SearchableCombobox.make_searchable(self.item_combo, item_list)
                print(f"  Set item dropdown values: {item_list[:3]}...")
            else:
                print("⚠️  No items found for dropdown")
            
            party_values = self.party_combo['values']
            item_values = self.item_combo['values']
            print(f"✅ Dropdown verification: {len(party_values)} parties, {len(item_values)} items")
            
        except Exception as e:
            print(f"❌ Error in PurchaseForm.load_initial_data(): {e}")
            import traceback
            traceback.print_exc()
            try:
                messagebox.showerror("Error", f"Failed to load initial data: {e}")
            except:
                pass
        
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
            item_text = self.item_var.get()
            qty = float(self.qty_var.get() or 0)
            rate = float(self.rate_var.get() or 0)
            
            if not item_text or qty <= 0 or rate <= 0:
                messagebox.showerror("Error", "Please fill all item details with valid values")
                return
                
            item_code = item_text.split(' - ')[0] if ' - ' in item_text else item_text
            item_name = item_text.split(' - ')[1] if ' - ' in item_text else item_text
            
            amount = qty * rate
            
            item_data = {
                'it_cd': item_code,
                'it_nm': item_name,
                'qty': qty,
                'rate': rate,
                'sal_amt': amount
            }
            
            self.items_data.append(item_data)
            
            self.items_tree.insert('', 'end', values=(
                item_code, item_name, f"{qty:.2f}", f"{rate:.2f}", f"{amount:.2f}"
            ))
            
            self.item_var.set('')
            self.qty_var.set('')
            self.rate_var.set('')
            
            self.update_total()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for quantity and rate")
            
    def delete_item(self, event):
        """Delete selected item"""
        selection = self.items_tree.selection()
        if selection:
            item_index = self.items_tree.index(selection[0])
            self.items_tree.delete(selection[0])
            del self.items_data[item_index]
            self.update_total()
            
    def update_total(self):
        """Update total amount"""
        total = sum(item['sal_amt'] for item in self.items_data)
        self.total_label.config(text=f"Total: ₹{total:.2f}")
        
    def save_purchase(self):
        """Save purchase entry"""
        try:
            if not self.items_data:
                messagebox.showerror("Error", "Please add at least one item")
                return
                
            party_text = self.party_var.get()
            if not party_text:
                messagebox.showerror("Error", "Please select a party")
                return
                
            party_code = party_text.split(' - ')[0] if ' - ' in party_text else party_text
            
            purchase_data = {
                'bill_no': int(self.bill_no_var.get()),
                'bill_date': self.bill_date_var.get(),
                'party_cd': party_code,
                'order_no': self.order_no_var.get(),
                'lr_no': self.lr_no_var.get(),
                'trans_cd': self.trans_var.get(),
                'exp1': float(self.exp1_var.get() or 0),
                'exp2': float(self.exp2_var.get() or 0),
                'exp3': float(self.exp3_var.get() or 0),
                'exp4': float(self.exp4_var.get() or 0),
                'exp5': float(self.exp5_var.get() or 0),
                'cash': float(self.cash_var.get() or 0),
                'other': 0
            }
            
            success, message = self.purchase_manager.create_purchase_entry(purchase_data, self.items_data)
            
            if success:
                messagebox.showinfo("Success", message)
                self.main_app.update_status(f"Purchase bill {purchase_data['bill_no']} saved successfully")
                self.clear_form()
                self.load_next_bill_number()
            else:
                messagebox.showerror("Error", message)
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save purchase: {e}")
            
    def clear_form(self):
        """Clear all form fields"""
        self.party_var.set('')
        self.order_no_var.set('')
        self.lr_no_var.set('')
        self.trans_var.set('')
        self.exp1_var.set('0')
        self.exp2_var.set('0')
        self.exp3_var.set('0')
        self.exp4_var.set('0')
        self.exp5_var.set('0')
        self.cash_var.set('0')
        self.item_var.set('')
        self.qty_var.set('')
        self.rate_var.set('')
        
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        self.items_data.clear()
        self.edit_mode = False
        self.original_bill_no = None
        self.window.title("Purchase Entry")
        self.update_total()
    
    def load_purchase_for_edit(self, bill_no, purchase_data):
        """Load existing purchase data for editing"""
        try:
            self.edit_mode = True
            self.original_bill_no = bill_no
            
            if purchase_data:
                first_record = purchase_data[0]
                self.party_var.set(f"{first_record.get('party_cd', '')} - {first_record.get('party_nm', '')}")
                self.order_no_var.set(first_record.get('order_no', ''))
                self.lr_no_var.set(first_record.get('lr_no', ''))
                self.trans_var.set(first_record.get('trans', ''))
                
                self.exp1_var.set(str(first_record.get('exp1', 0)))
                self.exp2_var.set(str(first_record.get('exp2', 0)))
                self.exp3_var.set(str(first_record.get('exp3', 0)))
                self.exp4_var.set(str(first_record.get('exp4', 0)))
                self.exp5_var.set(str(first_record.get('exp5', 0)))
                self.cash_var.set(str(first_record.get('cash', 0)))
                
                self.items_data = []
                for item in purchase_data:
                    self.items_data.append({
                        'it_cd': item.get('it_cd', ''),
                        'it_nm': item.get('it_nm', ''),
                        'qty': item.get('qty', 0),
                        'rate': item.get('rate', 0),
                        'sal_amt': item.get('sal_amt', 0)
                    })
                
                for item in self.items_tree.get_children():
                    self.items_tree.delete(item)
                
                for item in self.items_data:
                    self.items_tree.insert('', 'end', values=(
                        item.get('it_nm', ''),
                        f"{item.get('qty', 0):.2f}",
                        f"₹{item.get('rate', 0):.2f}",
                        f"₹{item.get('sal_amt', 0):.2f}"
                    ))
                
                self.update_total()
                self.window.title(f"Edit Purchase - Bill #{bill_no}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load purchase data: {e}")
