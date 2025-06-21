"""
Item management form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.queries import DatabaseQueries

class ItemForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Item Management")
        self.window.geometry("800x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        
        self.window.update_idletasks()
        self.window.after(100, self.load_items)
        
    def setup_form(self):
        """Setup the item management form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create item entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Item Details", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Item Code:").grid(row=0, column=0, sticky='w', pady=2)
        self.it_cd_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.it_cd_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Item Name:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.it_nm_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.it_nm_var, width=30).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Unit:").grid(row=1, column=0, sticky='w', pady=2)
        self.unit_var = tk.StringVar(value='KG')
        unit_combo = ttk.Combobox(entry_frame, textvariable=self.unit_var, width=12)
        unit_combo['values'] = ('KG', 'QUINTAL', 'TON', 'PIECE', 'BOX', 'BAG')
        unit_combo.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Rate:").grid(row=1, column=2, sticky='w', pady=2, padx=(20, 0))
        self.rate_var = tk.StringVar(value='0')
        ttk.Entry(entry_frame, textvariable=self.rate_var, width=15).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Category:").grid(row=2, column=0, sticky='w', pady=2)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(entry_frame, textvariable=self.category_var, width=20)
        category_combo['values'] = ('VEGETABLES', 'FRUITS', 'GRAINS', 'SPICES', 'OTHER')
        category_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
    def create_list_section(self, parent):
        """Create item list section"""
        list_frame = ttk.LabelFrame(parent, text="Items List", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)
        
        columns = ('Code', 'Name', 'Unit', 'Rate', 'Category')
        self.items_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.items_tree.heading(col, text=col)
            if col == 'Name':
                self.items_tree.column(col, width=250)
            elif col == 'Category':
                self.items_tree.column(col, width=120)
            else:
                self.items_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.items_tree.bind('<Double-1>', self.on_item_select)
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Item", 
                  command=self.save_item, 
                  style='Primary.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="New Item", 
                  command=self.clear_form, 
                  style='Success.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_items(self):
        """Load all items into the tree"""
        try:
            print(f"🔍 ItemForm.load_items() called")
            print(f"🔍 Tree widget exists: {hasattr(self, 'items_tree')}")
            print(f"🔍 Tree widget valid: {self.items_tree.winfo_exists() if hasattr(self, 'items_tree') else 'N/A'}")
            
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            items = self.queries.get_all_items()
            print(f"📦 Retrieved {len(items)} items from database")
            
            if not items:
                print("⚠️  No items found in database")
                return
            
            for i, item in enumerate(items):
                try:
                    tree_values = (
                        item['it_cd'],
                        item['it_nm'],
                        item.get('unit', 'KG'),
                        f"₹{item.get('rate', 0):.2f}",
                        item.get('category', '')
                    )
                    item_id = self.items_tree.insert('', 'end', values=tree_values)
                    print(f"  Added item {i+1}: {tree_values[0]} - {tree_values[1]} (ID: {item_id})")
                except Exception as item_error:
                    print(f"❌ Error adding item {i+1}: {item_error}")
                    continue
                
            tree_children = self.items_tree.get_children()
            print(f"✅ Tree now contains {len(tree_children)} items")
            
            if len(tree_children) != len(items):
                print(f"⚠️  Mismatch: Expected {len(items)} items, tree has {len(tree_children)}")
            
        except Exception as e:
            print(f"❌ Error in ItemForm.load_items(): {e}")
            import traceback
            traceback.print_exc()
            try:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Failed to load items: {e}")
            except:
                pass
            
    def on_search(self, event):
        """Handle search"""
        search_term = self.search_var.get()
        
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        if search_term:
            items = self.queries.search_items(search_term)
        else:
            items = self.queries.get_all_items()
            
        for item in items:
            self.items_tree.insert('', 'end', values=(
                item['it_cd'],
                item['it_nm'],
                item.get('unit', 'KG'),
                f"₹{item.get('rate', 0):.2f}",
                item.get('category', '')
            ))
            
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.items_tree.selection()
        if selection:
            item = self.items_tree.item(selection[0])
            values = item['values']
            
            self.it_cd_var.set(values[0])
            self.it_nm_var.set(values[1])
            self.unit_var.set(values[2])
            self.rate_var.set(values[3].replace('₹', ''))
            self.category_var.set(values[4])
            
    def save_item(self):
        """Save item data"""
        try:
            if not self.it_cd_var.get().strip():
                messagebox.showerror("Error", "Item code is required")
                return
                
            if not self.it_nm_var.get().strip():
                messagebox.showerror("Error", "Item name is required")
                return
                
            try:
                rate = float(self.rate_var.get() or 0)
                if rate < 0:
                    messagebox.showerror("Error", "Rate cannot be negative")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid rate")
                return
                
            item_data = {
                'it_cd': self.it_cd_var.get().strip().upper(),
                'it_nm': self.it_nm_var.get().strip(),
                'unit': self.unit_var.get().strip(),
                'rate': rate,
                'category': self.category_var.get().strip()
            }
            
            if self.queries.save_item(item_data):
                messagebox.showinfo("Success", "Item saved successfully")
                self.main_app.update_status(f"Item {item_data['it_cd']} saved successfully")
                self.load_items()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to save item")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid rate")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save item: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.it_cd_var.set('')
        self.it_nm_var.set('')
        self.unit_var.set('KG')
        self.rate_var.set('0')
        self.category_var.set('')
