"""
SALEPATTI - Enhanced Sales Entry Module with Advanced Features
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from database.queries import DatabaseQueries
from business.crate_utils import CrateUtils

class SalepattiForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        self.crate_utils = CrateUtils()
        
        self.window = tk.Toplevel(parent)
        self.window.title("SALEPATTI - Enhanced Sales Entry")
        self.window.geometry("1200x800")
        self.window.configure(bg=settings.colors['background'])
        
        self.items_list = []
        self.total_amount = 0.0
        
        self.setup_form()
        self.load_initial_data()
        
    def setup_form(self):
        """Setup the SALEPATTI form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        title_label = ttk.Label(main_frame, text="S A L E P A T T I   E N T R Y   M O D U L E", 
                               font=('Arial', 16, 'bold'), 
                               foreground=self.settings.colors['primary'])
        title_label.pack(pady=(0, 10))
        
        self.create_header_section(main_frame)
        self.create_items_section(main_frame)
        self.create_expenses_section(main_frame)
        self.create_crate_section(main_frame)
        self.create_commission_section(main_frame)
        self.create_buttons_section(main_frame)
        
        self.load_next_bill_number()
        
    def create_header_section(self, parent):
        """Create header section with bill details"""
        header_frame = ttk.LabelFrame(parent, text="Sales Details", padding=10)
        header_frame.pack(fill='x', pady=(0, 10))
        
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side='right', fill='x', expand=True, padx=(20, 0))
        
        ttk.Label(left_frame, text="Bill No:").grid(row=0, column=0, sticky='w', pady=2)
        self.bill_no_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.bill_no_var, width=15, state='readonly').grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Date:").grid(row=1, column=0, sticky='w', pady=2)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(left_frame, textvariable=self.date_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(left_frame, text="Party:").grid(row=2, column=0, sticky='w', pady=2)
        self.party_var = tk.StringVar()
        self.party_combo = ttk.Combobox(left_frame, textvariable=self.party_var, width=30)
        self.party_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        self.party_combo.bind('<KeyRelease>', self.on_party_search)
        
        ttk.Label(right_frame, text="Transport:").grid(row=0, column=0, sticky='w', pady=2)
        self.transport_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.transport_var, width=20).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(right_frame, text="Vehicle No:").grid(row=1, column=0, sticky='w', pady=2)
        self.vehicle_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.vehicle_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(right_frame, text="Agent:").grid(row=2, column=0, sticky='w', pady=2)
        self.agent_var = tk.StringVar()
        self.agent_combo = ttk.Combobox(right_frame, textvariable=self.agent_var, width=20)
        self.agent_combo.grid(row=2, column=1, padx=5, pady=2)
        
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
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=8)
        
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
        
    def create_expenses_section(self, parent):
        """Create expenses section"""
        expenses_frame = ttk.LabelFrame(parent, text="Expenses & Charges", padding=10)
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
        self.crate_combo = ttk.Combobox(left_crate, textvariable=self.crate_type_var, 
                                       values=self.crate_utils.get_crate_types(), width=20)
        self.crate_combo.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(right_crate, text="Crate Bhada:").grid(row=0, column=0, sticky='w', pady=2)
        self.crate_bhada_var = tk.StringVar(value='0')
        ttk.Entry(right_crate, textvariable=self.crate_bhada_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(right_crate, text="Distance (KM):").grid(row=1, column=0, sticky='w', pady=2)
        self.distance_var = tk.StringVar(value='0')
        ttk.Entry(right_crate, textvariable=self.distance_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(crate_frame, text="Calculate Freight", 
                  command=self.calculate_freight_charges,
                  style='Success.TButton').pack(side='right', padx=5)
    
    def create_commission_section(self, parent):
        """Create commission calculation section"""
        commission_frame = ttk.LabelFrame(parent, text="Commission & Agent Details", padding=10)
        commission_frame.pack(fill='x', pady=(0, 10))
        
        left_comm = ttk.Frame(commission_frame)
        left_comm.pack(side='left', fill='x', expand=True)
        
        right_comm = ttk.Frame(commission_frame)
        right_comm.pack(side='right', fill='x', expand=True, padx=(20, 0))
        
        ttk.Label(left_comm, text="Commission %:").grid(row=0, column=0, sticky='w', pady=2)
        self.commission_percent_var = tk.StringVar(value='2.5')
        ttk.Entry(left_comm, textvariable=self.commission_percent_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(left_comm, text="Commission Amount:").grid(row=1, column=0, sticky='w', pady=2)
        self.commission_amount_var = tk.StringVar(value='0')
        ttk.Entry(left_comm, textvariable=self.commission_amount_var, width=10, state='readonly').grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(right_comm, text="Agent Code:").grid(row=0, column=0, sticky='w', pady=2)
        self.agent_code_var = tk.StringVar()
        ttk.Entry(right_comm, textvariable=self.agent_code_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Button(commission_frame, text="Calculate Commission", 
                  command=self.calculate_commission,
                  style='Primary.TButton').pack(side='right', padx=5)
    
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save SALEPATTI", 
                  command=self.save_salepatti,
                  style='Primary.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Print Preview", 
                  command=self.print_preview,
                  style='Success.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_form,
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy,
                  style='Modern.TButton').pack(side='right', padx=5)
        
        self.total_label = ttk.Label(button_frame, text="Grand Total: ₹0.00", 
                                   font=('Arial', 14, 'bold'),
                                   foreground=self.settings.colors['primary'])
        self.total_label.pack(side='left')
    
    def load_next_bill_number(self):
        """Load next bill number"""
        try:
            next_bill = self.db_manager.get_next_bill_number('salepatti')
            self.bill_no_var.set(str(next_bill))
        except Exception as e:
            print(f"Error loading next bill number: {e}")
            self.bill_no_var.set('1')
    
    def load_initial_data(self):
        """Load initial data for dropdowns"""
        try:
            parties = self.queries.get_all_parties()
            if parties:
                party_list = [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
                self.party_combo['values'] = party_list
            
            items = self.queries.get_all_items()
            if items:
                item_list = [f"{i['it_cd']} - {i['it_nm']}" for i in items]
                self.item_combo['values'] = item_list
            
            agents = self.queries.get_all_agents()
            if agents:
                agent_list = [f"{a['agent_cd']} - {a['agent_nm']}" for a in agents]
                self.agent_combo['values'] = agent_list
                
        except Exception as e:
            print(f"Error loading initial data: {e}")
    
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
            
            self.update_totals()
            
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
            self.update_totals()
    
    def calculate_freight_charges(self):
        """Calculate freight charges based on crates and distance"""
        try:
            total_crates = int(self.total_crates_var.get() or 0)
            distance = float(self.distance_var.get() or 0)
            crate_type = self.crate_type_var.get()
            
            if total_crates > 0 and distance > 0:
                freight_charges = self.crate_utils.calculate_freight_by_distance(total_crates, distance)
                self.crate_bhada_var.set(f"{freight_charges:.2f}")
                
                current_exp2 = float(self.exp2_var.get() or 0)
                total_bhada = current_exp2 + freight_charges
                self.exp2_var.set(f"{total_bhada:.2f}")
                
                self.update_totals()
                messagebox.showinfo("Success", f"Freight charges calculated: ₹{freight_charges:.2f}")
            else:
                messagebox.showwarning("Warning", "Please enter valid crate count and distance")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
    
    def calculate_commission(self):
        """Calculate commission based on total amount"""
        try:
            commission_percent = float(self.commission_percent_var.get() or 0)
            total_amount = sum(item['amount'] for item in self.items_list)
            
            commission_amount = (total_amount * commission_percent) / 100
            self.commission_amount_var.set(f"{commission_amount:.2f}")
            
            current_exp1 = float(self.exp1_var.get() or 0)
            total_tapaal = current_exp1 + commission_amount
            self.exp1_var.set(f"{total_tapaal:.2f}")
            
            self.update_totals()
            messagebox.showinfo("Success", f"Commission calculated: ₹{commission_amount:.2f}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid commission percentage")
    
    def update_totals(self):
        """Update total amounts"""
        try:
            items_total = sum(item['amount'] for item in self.items_list)
            expenses_total = sum([
                float(self.exp1_var.get() or 0),
                float(self.exp2_var.get() or 0),
                float(self.exp3_var.get() or 0),
                float(self.exp4_var.get() or 0),
                float(self.exp5_var.get() or 0)
            ])
            
            grand_total = items_total + expenses_total
            self.total_label.config(text=f"Grand Total: ₹{grand_total:.2f}")
            
        except ValueError:
            self.total_label.config(text="Grand Total: ₹0.00")
    
    def save_salepatti(self):
        """Save SALEPATTI entry"""
        try:
            if not self.party_var.get():
                messagebox.showerror("Error", "Please select a party")
                return
                
            if not self.items_list:
                messagebox.showerror("Error", "Please add at least one item")
                return
                
            party_code = self.party_var.get().split(' - ')[0]
            agent_code = self.agent_var.get().split(' - ')[0] if ' - ' in self.agent_var.get() else self.agent_var.get()
            
            salepatti_data = {
                'bill_no': int(self.bill_no_var.get()),
                'bill_dt': self.date_var.get(),
                'party_cd': party_code,
                'transport': self.transport_var.get(),
                'vehicle_no': self.vehicle_var.get(),
                'agent_cd': agent_code,
                'exp1': float(self.exp1_var.get() or 0),
                'exp2': float(self.exp2_var.get() or 0),
                'exp3': float(self.exp3_var.get() or 0),
                'exp4': float(self.exp4_var.get() or 0),
                'exp5': float(self.exp5_var.get() or 0),
                'cash': float(self.cash_var.get() or 0),
                'total_crates': int(self.total_crates_var.get() or 0),
                'crate_type': self.crate_type_var.get(),
                'crate_bhada': float(self.crate_bhada_var.get() or 0),
                'commission_percent': float(self.commission_percent_var.get() or 0),
                'commission_amount': float(self.commission_amount_var.get() or 0),
                'items': self.items_list
            }
            
            if self.queries.save_sale(salepatti_data):
                messagebox.showinfo("Success", f"SALEPATTI {salepatti_data['bill_no']} saved successfully")
                self.main_app.update_status(f"SALEPATTI {salepatti_data['bill_no']} saved successfully")
                self.clear_form()
                self.load_next_bill_number()
            else:
                messagebox.showerror("Error", "Failed to save SALEPATTI")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save SALEPATTI: {e}")
    
    def print_preview(self):
        """Show print preview"""
        if not self.items_list:
            messagebox.showwarning("Warning", "Please add items before printing")
            return
            
        preview_window = tk.Toplevel(self.window)
        preview_window.title("SALEPATTI Print Preview")
        preview_window.geometry("600x800")
        
        text_widget = tk.Text(preview_window, wrap='word', font=('Courier', 10))
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        content = self.generate_salepatti_text()
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
    
    def print_document(self, content):
        """Print document using system print dialog"""
        try:
            import tempfile
            import os
            import subprocess
            import platform
            
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
    
    def generate_salepatti_text(self):
        """Generate SALEPATTI text for printing"""
        lines = []
        lines.append("=" * 70)
        lines.append("S A L E P A T T I   E N T R Y")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Bill No    : {self.bill_no_var.get()}")
        lines.append(f"Date       : {self.date_var.get()}")
        lines.append(f"Party      : {self.party_var.get()}")
        lines.append(f"Transport  : {self.transport_var.get()}")
        lines.append(f"Vehicle No : {self.vehicle_var.get()}")
        lines.append(f"Agent      : {self.agent_var.get()}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("ITEM DETAILS")
        lines.append("-" * 70)
        lines.append(f"{'Code':<10} {'Item Name':<25} {'Qty':<8} {'Rate':<10} {'Amount':<10}")
        lines.append("-" * 70)
        
        for item in self.items_list:
            lines.append(f"{item['item_code']:<10} {item['item_name']:<25} {item['quantity']:<8.2f} {item['rate']:<10.2f} {item['amount']:<10.2f}")
        
        items_total = sum(item['amount'] for item in self.items_list)
        lines.append("-" * 70)
        lines.append(f"{'Items Total:':<55} ₹{items_total:.2f}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("EXPENSES & CHARGES")
        lines.append("-" * 70)
        lines.append(f"Tapaal (Commission): ₹{self.exp1_var.get()}")
        lines.append(f"Bhada (Freight)   : ₹{self.exp2_var.get()}")
        lines.append(f"Rail Freight      : ₹{self.exp3_var.get()}")
        lines.append(f"Hamali (Loading)  : ₹{self.exp4_var.get()}")
        lines.append(f"Others            : ₹{self.exp5_var.get()}")
        lines.append(f"Advance           : ₹{self.cash_var.get()}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("CRATE DETAILS")
        lines.append("-" * 70)
        lines.append(f"Total Crates      : {self.total_crates_var.get()}")
        lines.append(f"Crate Type        : {self.crate_type_var.get()}")
        lines.append(f"Crate Bhada       : ₹{self.crate_bhada_var.get()}")
        lines.append(f"Distance          : {self.distance_var.get()} KM")
        lines.append("")
        lines.append("-" * 70)
        lines.append("COMMISSION DETAILS")
        lines.append("-" * 70)
        lines.append(f"Commission %      : {self.commission_percent_var.get()}%")
        lines.append(f"Commission Amount : ₹{self.commission_amount_var.get()}")
        lines.append("")
        
        expenses_total = sum([
            float(self.exp1_var.get() or 0),
            float(self.exp2_var.get() or 0),
            float(self.exp3_var.get() or 0),
            float(self.exp4_var.get() or 0),
            float(self.exp5_var.get() or 0)
        ])
        grand_total = items_total + expenses_total
        
        lines.append("=" * 70)
        lines.append(f"Total Expenses    : ₹{expenses_total:.2f}")
        lines.append(f"GRAND TOTAL       : ₹{grand_total:.2f}")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("=" * 70)
        
        return '\n'.join(lines)
    
    def clear_form(self):
        """Clear form fields"""
        self.party_var.set('')
        self.transport_var.set('')
        self.vehicle_var.set('')
        self.agent_var.set('')
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
        self.distance_var.set('0')
        self.commission_percent_var.set('2.5')
        self.commission_amount_var.set('0')
        self.agent_code_var.set('')
        
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        self.items_list.clear()
        self.update_totals()
