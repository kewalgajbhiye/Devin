"""
Lot Management form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database.queries import DatabaseQueries

class LotManagementForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Lot Management")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_lots()
        
    def setup_form(self):
        """Setup the lot management form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create lot entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Lot Entry", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Lot No:").grid(row=0, column=0, sticky='w', pady=2)
        self.lot_no_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.lot_no_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Lot Date:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.lot_date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(entry_frame, textvariable=self.lot_date_var, width=15).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Item:").grid(row=1, column=0, sticky='w', pady=2)
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(entry_frame, textvariable=self.item_var, width=30)
        self.item_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Quantity:").grid(row=2, column=0, sticky='w', pady=2)
        self.qty_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.qty_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Rate:").grid(row=2, column=2, sticky='w', pady=2, padx=(20, 0))
        self.rate_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.rate_var, width=15).grid(row=2, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Expiry Date:").grid(row=3, column=0, sticky='w', pady=2)
        self.expiry_date_var = tk.StringVar(value=(datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y'))
        ttk.Entry(entry_frame, textvariable=self.expiry_date_var, width=15).grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Status:").grid(row=3, column=2, sticky='w', pady=2, padx=(20, 0))
        self.status_var = tk.StringVar(value='ACTIVE')
        status_options = ['ACTIVE', 'SOLD', 'EXPIRED', 'DAMAGED']
        self.status_combo = ttk.Combobox(entry_frame, textvariable=self.status_var, values=status_options, width=15)
        self.status_combo.grid(row=3, column=3, padx=5, pady=2)
        
        self.load_items()
        
    def create_list_section(self, parent):
        """Create lots list section"""
        list_frame = ttk.LabelFrame(parent, text="Lot Records", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Lot No', 'Item', 'Quantity', 'Rate', 'Lot Date', 'Expiry Date', 'Status')
        self.lot_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.lot_tree.heading(col, text=col)
            if col == 'Item':
                self.lot_tree.column(col, width=200)
            elif col in ['Quantity', 'Rate']:
                self.lot_tree.column(col, width=100)
            else:
                self.lot_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.lot_tree.yview)
        self.lot_tree.configure(yscrollcommand=scrollbar.set)
        
        self.lot_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Lot", 
                  command=self.save_lot, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_form, 
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Expiry Alert", 
                  command=self.show_expiry_alert, 
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
            
    def load_lot_stock(self):
        """Load lot stock"""
        try:
            for item in self.lot_tree.get_children():
                self.lot_tree.delete(item)
            
            lots = self.queries.get_all_lot_stock()
            
            for lot in lots:
                item_name = lot.get('it_nm', '') or ''
                expiry_date = lot.get('expiry_date', '') or ''
                
                self.lot_tree.insert('', 'end', values=(
                    lot['lot_no'],
                    item_name,
                    f"{lot['qty']:.2f}",
                    f"₹{lot['rate']:.2f}",
                    lot['lot_date'],
                    expiry_date,
                    lot['status']
                ))
                
            self.main_app.update_status(f"Loaded {len(lots)} lot records")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load lot stock: {e}")
            
    def on_lot_select(self, event):
        """Handle lot selection"""
        try:
            selection = self.lot_tree.selection()
            if selection:
                item = self.lot_tree.item(selection[0])
                values = item['values']
                
                self.lot_no_var.set(values[0])
                self.qty_var.set(values[2])
                rate = values[3].replace('₹', '')
                self.rate_var.set(rate)
                self.lot_date_var.set(values[4])
                self.expiry_date_var.set(values[5])
                self.status_var.set(values[6])
        except Exception as e:
            print(f"Error selecting lot: {e}")
            
    def save_lot(self):
        """Save lot stock"""
        try:
            if not self.lot_no_var.get().strip():
                messagebox.showerror("Error", "Please enter lot number")
                return
            
            if not self.item_var.get():
                messagebox.showerror("Error", "Please select an item")
                return
            
            if not self.qty_var.get().strip():
                messagebox.showerror("Error", "Please enter quantity")
                return
            
            qty = float(self.qty_var.get())
            rate = float(self.rate_var.get() or 0)
            item_code = self.item_var.get().split(' - ')[0]
            
            expiry_date = None
            if self.expiry_date_var.get():
                expiry_date = datetime.strptime(self.expiry_date_var.get(), '%d/%m/%Y').date()
            
            lot_data = {
                'lot_no': self.lot_no_var.get(),
                'it_cd': item_code,
                'qty': qty,
                'rate': rate,
                'lot_date': datetime.strptime(self.lot_date_var.get(), '%d/%m/%Y').date(),
                'expiry_date': expiry_date,
                'status': self.status_var.get()
            }
            
            if self.queries.save_lot_stock(lot_data):
                messagebox.showinfo("Success", "Lot stock saved successfully")
                self.clear_form()
                self.load_lot_stock()
            else:
                messagebox.showerror("Error", "Failed to save lot stock")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid quantity and rate")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save lot: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.lot_no_var.set('')
        self.lot_date_var.set(datetime.now().strftime('%d/%m/%Y'))
        self.item_var.set('')
        self.qty_var.set('')
        self.rate_var.set('')
        self.expiry_date_var.set('')
        self.status_var.set('ACTIVE')
        
    def generate_lot_no(self):
        """Generate lot number"""
        try:
            import time
            lot_no = f"LOT{int(time.time())}"
            self.lot_no_var.set(lot_no)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate lot number: {e}")
            
    def show_expiry_report(self):
        """Show expiry report"""
        try:
            report_window = tk.Toplevel(self.window)
            report_window.title("Expiry Report")
            report_window.geometry("800x600")
            
            main_frame = ttk.Frame(report_window)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            ttk.Label(main_frame, text="Lot Expiry Report", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            columns = ('Lot No', 'Item', 'Quantity', 'Expiry Date', 'Days Left', 'Status')
            tree = ttk.Treeview(main_frame, columns=columns, show='headings')
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)
            
            scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            lots = self.queries.get_all_lot_stock()
            today = datetime.now().date()
            
            for lot in lots:
                if lot.get('expiry_date'):
                    try:
                        if isinstance(lot['expiry_date'], str):
                            expiry_date = datetime.strptime(lot['expiry_date'], '%Y-%m-%d').date()
                        else:
                            expiry_date = lot['expiry_date']
                        
                        days_left = (expiry_date - today).days
                        status = "EXPIRED" if days_left < 0 else "EXPIRING SOON" if days_left <= 7 else "OK"
                        
                        tree.insert('', 'end', values=(
                            lot['lot_no'],
                            lot.get('it_nm', ''),
                            f"{lot['qty']:.2f}",
                            expiry_date.strftime('%d/%m/%Y'),
                            days_left,
                            status
                        ))
                    except:
                        continue
            
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill='x', pady=(10, 0))
            
            ttk.Button(button_frame, text="Export to PDF", 
                      command=lambda: self.export_expiry_report(tree), 
                      style='Warning.TButton').pack(side='right', padx=5)
            
            ttk.Button(button_frame, text="Close", 
                      command=report_window.destroy, 
                      style='Modern.TButton').pack(side='right', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show expiry report: {e}")
            
    def load_lots(self):
        """Load lot records"""
        try:
            for item in self.lot_tree.get_children():
                self.lot_tree.delete(item)
            
            lots = self.queries.get_all_lot_stock()
            
            for lot in lots:
                item_name = lot.get('it_nm', '') or ''
                
                self.lot_tree.insert('', 'end', values=(
                    lot['lot_no'],
                    item_name,
                    f"{lot['qty']:.2f}",
                    f"₹{lot['rate']:.2f}",
                    lot['lot_date'],
                    lot['expiry_date'] or '',
                    lot['status']
                ))
                
            self.main_app.update_status(f"Loaded {len(lots)} lot records")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load lots: {e}")
            
    def save_lot(self):
        """Save lot record"""
        try:
            if not self.lot_no_var.get().strip():
                messagebox.showerror("Error", "Please enter lot number")
                return
            
            if not self.item_var.get():
                messagebox.showerror("Error", "Please select an item")
                return
            
            if not self.qty_var.get().strip():
                messagebox.showerror("Error", "Please enter quantity")
                return
            
            qty = float(self.qty_var.get())
            rate = float(self.rate_var.get() or 0)
            item_code = self.item_var.get().split(' - ')[0]
            
            expiry_date = None
            if self.expiry_date_var.get().strip():
                expiry_date = datetime.strptime(self.expiry_date_var.get(), '%d/%m/%Y').date()
            
            lot_data = {
                'lot_no': self.lot_no_var.get(),
                'it_cd': item_code,
                'qty': qty,
                'rate': rate,
                'lot_date': datetime.strptime(self.lot_date_var.get(), '%d/%m/%Y').date(),
                'expiry_date': expiry_date,
                'status': self.status_var.get()
            }
            
            if self.queries.save_lot_stock(lot_data):
                messagebox.showinfo("Success", "Lot record saved successfully")
                self.clear_form()
                self.load_lots()
            else:
                messagebox.showerror("Error", "Failed to save lot record")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid quantity and rate")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save lot: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.lot_no_var.set('')
        self.lot_date_var.set(datetime.now().strftime('%d/%m/%Y'))
        self.item_var.set('')
        self.qty_var.set('')
        self.rate_var.set('')
        self.expiry_date_var.set((datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y'))
        self.status_var.set('ACTIVE')
        
    def show_expiry_alert(self):
        """Show expiry alert for lots"""
        try:
            messagebox.showinfo("Expiry Alert", "Expiry alert functionality will be implemented in the next version.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show expiry alert: {e}")
