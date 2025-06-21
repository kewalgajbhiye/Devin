"""
Party management form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.queries import DatabaseQueries

class PartyForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Party Management")
        self.window.geometry("800x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        
        self.window.update_idletasks()
        self.window.after(100, self.load_parties)
        
    def setup_form(self):
        """Setup the party management form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create party entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Party Details", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Party Code:").grid(row=0, column=0, sticky='w', pady=2)
        self.party_cd_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.party_cd_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Party Name:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.party_nm_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.party_nm_var, width=30).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Place:").grid(row=1, column=0, sticky='w', pady=2)
        self.place_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.place_var, width=20).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Phone:").grid(row=1, column=2, sticky='w', pady=2, padx=(20, 0))
        self.phone_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.phone_var, width=15).grid(row=1, column=3, padx=5, pady=2)
        
    def create_list_section(self, parent):
        """Create party list section"""
        list_frame = ttk.LabelFrame(parent, text="Parties List", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)
        
        columns = ('Code', 'Name', 'Place', 'Phone', 'Balance')
        self.parties_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.parties_tree.heading(col, text=col)
            if col == 'Name':
                self.parties_tree.column(col, width=200)
            elif col == 'Place':
                self.parties_tree.column(col, width=150)
            else:
                self.parties_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.parties_tree.yview)
        self.parties_tree.configure(yscrollcommand=scrollbar.set)
        
        self.parties_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.parties_tree.bind('<Double-1>', self.on_party_select)
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Party", 
                  command=self.save_party, 
                  style='Primary.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="New Party", 
                  command=self.clear_form, 
                  style='Success.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_parties(self):
        """Load all parties into the tree"""
        try:
            print(f"🔍 PartyForm.load_parties() called")
            print(f"🔍 Tree widget exists: {hasattr(self, 'parties_tree')}")
            print(f"🔍 Tree widget valid: {self.parties_tree.winfo_exists() if hasattr(self, 'parties_tree') else 'N/A'}")
            
            for item in self.parties_tree.get_children():
                self.parties_tree.delete(item)
            
            parties = self.queries.get_all_parties()
            print(f"👥 Retrieved {len(parties)} parties from database")
            
            if not parties:
                print("⚠️  No parties found in database")
                return
            
            for i, party in enumerate(parties):
                try:
                    balance = party.get('ytd_dr', 0) - party.get('ytd_cr', 0)
                    tree_values = (
                        party['party_cd'],
                        party['party_nm'],
                        party.get('place', ''),
                        party.get('phone', ''),
                        f"₹{balance:.2f}"
                    )
                    party_id = self.parties_tree.insert('', 'end', values=tree_values)
                    print(f"  Added party {i+1}: {tree_values[0]} - {tree_values[1]} (ID: {party_id})")
                except Exception as party_error:
                    print(f"❌ Error adding party {i+1}: {party_error}")
                    continue
                
            tree_children = self.parties_tree.get_children()
            print(f"✅ Tree now contains {len(tree_children)} parties")
            
            if len(tree_children) != len(parties):
                print(f"⚠️  Mismatch: Expected {len(parties)} parties, tree has {len(tree_children)}")
            
        except Exception as e:
            print(f"❌ Error in PartyForm.load_parties(): {e}")
            import traceback
            traceback.print_exc()
            try:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Failed to load parties: {e}")
            except:
                pass
            
    def on_search(self, event):
        """Handle search"""
        search_term = self.search_var.get()
        
        for item in self.parties_tree.get_children():
            self.parties_tree.delete(item)
            
        if search_term:
            parties = self.queries.search_parties(search_term)
        else:
            parties = self.queries.get_all_parties()
            
        for party in parties:
            balance = party.get('ytd_dr', 0) - party.get('ytd_cr', 0)
            self.parties_tree.insert('', 'end', values=(
                party['party_cd'],
                party['party_nm'],
                party.get('place', ''),
                party.get('phone', ''),
                f"₹{balance:.2f}"
            ))
            
    def on_party_select(self, event):
        """Handle party selection"""
        selection = self.parties_tree.selection()
        if selection:
            item = self.parties_tree.item(selection[0])
            values = item['values']
            
            self.party_cd_var.set(values[0])
            self.party_nm_var.set(values[1])
            self.place_var.set(values[2])
            self.phone_var.set(values[3])
            
    def save_party(self):
        """Save party data"""
        try:
            if not self.party_cd_var.get().strip():
                messagebox.showerror("Error", "Party code is required")
                return
                
            if not self.party_nm_var.get().strip():
                messagebox.showerror("Error", "Party name is required")
                return
                
            phone = self.phone_var.get().strip()
            if phone and not phone.replace(' ', '').replace('-', '').isdigit():
                messagebox.showerror("Error", "Please enter a valid phone number")
                return
                
            party_data = {
                'party_cd': self.party_cd_var.get().strip().upper(),
                'party_nm': self.party_nm_var.get().strip(),
                'place': self.place_var.get().strip(),
                'phone': phone
            }
            
            if self.queries.save_party(party_data):
                messagebox.showinfo("Success", "Party saved successfully")
                self.main_app.update_status(f"Party {party_data['party_cd']} saved successfully")
                self.load_parties()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to save party")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save party: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.party_cd_var.set('')
        self.party_nm_var.set('')
        self.place_var.set('')
        self.phone_var.set('')
