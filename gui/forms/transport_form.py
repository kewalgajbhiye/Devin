"""
Transport Management form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.queries import DatabaseQueries

class TransportForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Transport Management")
        self.window.geometry("900x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_transports()
        
    def setup_form(self):
        """Setup the transport form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create transport entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Transport Company Details", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Transport Code:").grid(row=0, column=0, sticky='w', pady=2)
        self.trans_cd_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.trans_cd_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Company Name:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.name_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.name_var, width=30).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Destination:").grid(row=1, column=0, sticky='w', pady=2)
        self.dest_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.dest_var, width=20).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Phone:").grid(row=1, column=2, sticky='w', pady=2, padx=(20, 0))
        self.phone_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.phone_var, width=15).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Address:").grid(row=2, column=0, sticky='w', pady=2)
        self.address_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.address_var, width=50).grid(row=2, column=1, columnspan=3, padx=5, pady=2, sticky='ew')
        
    def create_list_section(self, parent):
        """Create transport list section"""
        list_frame = ttk.LabelFrame(parent, text="Transport Companies", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Code', 'Company Name', 'Destination', 'Phone', 'Address')
        self.transport_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.transport_tree.heading(col, text=col)
            if col == 'Company Name':
                self.transport_tree.column(col, width=200)
            elif col == 'Address':
                self.transport_tree.column(col, width=250)
            else:
                self.transport_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.transport_tree.yview)
        self.transport_tree.configure(yscrollcommand=scrollbar.set)
        
        self.transport_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.transport_tree.bind('<Double-1>', self.on_transport_select)
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Transport", 
                  command=self.save_transport, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_form, 
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Delete", 
                  command=self.delete_transport, 
                  style='Warning.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_transports(self):
        """Load transport companies"""
        try:
            for item in self.transport_tree.get_children():
                self.transport_tree.delete(item)
            
            transports = self.queries.get_all_transports()
            
            for transport in transports:
                self.transport_tree.insert('', 'end', values=(
                    transport['trans_cd'],
                    transport['name'],
                    transport['dest'] or '',
                    transport['phone'] or '',
                    transport['address'] or ''
                ))
                
            self.main_app.update_status(f"Loaded {len(transports)} transport companies")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transports: {e}")
            
    def on_transport_select(self, event):
        """Handle transport selection"""
        try:
            selection = self.transport_tree.selection()
            if selection:
                item = self.transport_tree.item(selection[0])
                values = item['values']
                
                self.trans_cd_var.set(values[0])
                self.name_var.set(values[1])
                self.dest_var.set(values[2])
                self.phone_var.set(values[3])
                self.address_var.set(values[4])
        except Exception as e:
            print(f"Error selecting transport: {e}")
            
    def save_transport(self):
        """Save transport company"""
        try:
            if not self.trans_cd_var.get().strip():
                messagebox.showerror("Error", "Please enter transport code")
                return
            
            if not self.name_var.get().strip():
                messagebox.showerror("Error", "Please enter company name")
                return
            
            transport_data = {
                'trans_cd': self.trans_cd_var.get(),
                'name': self.name_var.get(),
                'dest': self.dest_var.get(),
                'phone': self.phone_var.get(),
                'address': self.address_var.get()
            }
            
            if self.queries.save_transport(transport_data):
                messagebox.showinfo("Success", "Transport company saved successfully")
                self.clear_form()
                self.load_transports()
            else:
                messagebox.showerror("Error", "Failed to save transport company")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save transport: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.trans_cd_var.set('')
        self.name_var.set('')
        self.dest_var.set('')
        self.phone_var.set('')
        self.address_var.set('')
        
    def delete_transport(self):
        """Delete selected transport"""
        try:
            selection = self.transport_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a transport company to delete")
                return
            
            item = self.transport_tree.item(selection[0])
            trans_cd = item['values'][0]
            company_name = item['values'][1]
            
            if messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete transport company '{company_name}'?\n\nThis action cannot be undone."):
                
                if self.queries.delete_transport(trans_cd):
                    messagebox.showinfo("Success", "Transport company deleted successfully")
                    self.clear_form()
                    self.load_transports()
                    self.main_app.update_status(f"Deleted transport company: {company_name}")
                else:
                    messagebox.showerror("Error", "Failed to delete transport company")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete transport: {e}")
