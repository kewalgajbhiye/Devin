"""
Independent Crate Management Form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.queries import DatabaseQueries

class CrateManagementForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Crate Management")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_data()
        
    def setup_form(self):
        """Setup the crate management form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_party_selection(main_frame)
        self.create_crate_entry_section(main_frame)
        self.create_crate_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_party_selection(self, parent):
        """Create party selection section"""
        party_frame = ttk.LabelFrame(parent, text="Select Party", padding=10)
        party_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(party_frame, text="Party:").grid(row=0, column=0, sticky='w', pady=5)
        self.party_var = tk.StringVar()
        from gui.components.searchable_combobox import SearchableCombobox
        self.party_combo = SearchableCombobox.create_searchable_combobox(
            party_frame, self.party_var, [], width=40)
        self.party_combo.grid(row=0, column=1, padx=10, pady=5, sticky='ew')
        self.party_combo.bind('<<ComboboxSelected>>', self.on_party_select)
        
        ttk.Button(party_frame, text="Load Party Data", 
                  command=self.load_party_crate_data,
                  style='Primary.TButton').grid(row=0, column=2, padx=10, pady=5)
        
        ttk.Button(party_frame, text="Import Crate Data", 
                  command=self.import_crate_data,
                  style='Warning.TButton').grid(row=0, column=3, padx=10, pady=5)
        
        party_frame.columnconfigure(1, weight=1)
        
    def create_crate_entry_section(self, parent):
        """Create crate entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Crate Details", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        left_frame = ttk.Frame(entry_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        right_frame = ttk.Frame(entry_frame)
        right_frame.pack(side='right', fill='x', expand=True, padx=(20, 0))
        
        ttk.Label(left_frame, text="Total Crates:").grid(row=0, column=0, sticky='w', pady=5)
        self.total_crates_var = tk.StringVar(value='0')
        ttk.Entry(left_frame, textvariable=self.total_crates_var, width=15).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(left_frame, text="Crates Given:").grid(row=1, column=0, sticky='w', pady=5)
        self.crates_given_var = tk.StringVar(value='0')
        ttk.Entry(left_frame, textvariable=self.crates_given_var, width=15).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(left_frame, text="Crates Received:").grid(row=2, column=0, sticky='w', pady=5)
        self.crates_received_var = tk.StringVar(value='0')
        ttk.Entry(left_frame, textvariable=self.crates_received_var, width=15).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(right_frame, text="Crate Type:").grid(row=0, column=0, sticky='w', pady=5)
        self.crate_type_var = tk.StringVar(value='Standard')
        crate_types = ['Standard', 'Plastic', 'Wooden', 'Metal', 'Jute Bags - 50 KG', 'Plastic Crates - 20 KG']
        ttk.Combobox(right_frame, textvariable=self.crate_type_var, 
                    values=crate_types, width=20).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(right_frame, text="Remaining Crates:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.remaining_label = ttk.Label(right_frame, text="0", font=('Arial', 12, 'bold'), foreground='blue')
        self.remaining_label.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Button(right_frame, text="Calculate Remaining", 
                  command=self.calculate_remaining,
                  style='Success.TButton').grid(row=2, column=0, columnspan=2, pady=10)
        
    def create_crate_list_section(self, parent):
        """Create crate list section"""
        list_frame = ttk.LabelFrame(parent, text="All Party Crate Records", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Party', 'Total', 'Given', 'Received', 'Remaining', 'Type', 'Last Updated')
        self.crate_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.crate_tree.heading(col, text=col)
            if col in ['Total', 'Given', 'Received', 'Remaining']:
                self.crate_tree.column(col, width=80, anchor='center')
            elif col == 'Type':
                self.crate_tree.column(col, width=120)
            elif col == 'Last Updated':
                self.crate_tree.column(col, width=100)
            else:
                self.crate_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.crate_tree.yview)
        self.crate_tree.configure(yscrollcommand=scrollbar.set)
        
        self.crate_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.crate_tree.bind('<<TreeviewSelect>>', self.on_crate_select)
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save/Update Crate Data", 
                  command=self.save_crate_data,
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear Form", 
                  command=self.clear_form,
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Refresh List", 
                  command=self.load_crate_list,
                  style='Success.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy,
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_data(self):
        """Load initial data"""
        try:
            parties = self.queries.get_all_parties()
            party_list = [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
            self.party_combo['values'] = party_list
            
            from gui.components.searchable_combobox import SearchableCombobox
            SearchableCombobox.make_searchable(self.party_combo, party_list)
            
            self.load_crate_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            
    def load_crate_list(self):
        """Load all crate management records"""
        try:
            for item in self.crate_tree.get_children():
                self.crate_tree.delete(item)
            
            crate_records = self.queries.get_all_crate_management()
            
            for record in crate_records:
                self.crate_tree.insert('', 'end', values=(
                    record.get('party_nm', 'Unknown'),
                    record.get('total_crates', 0),
                    record.get('crates_given', 0),
                    record.get('crates_received', 0),
                    record.get('remaining_crates', 0),
                    record.get('crate_type', 'Standard'),
                    record.get('last_updated', '')
                ))
                
            self.main_app.update_status(f"Loaded {len(crate_records)} crate records")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load crate records: {e}")
            
    def on_party_select(self, event=None):
        """Handle party selection"""
        self.load_party_crate_data()
        
    def load_party_crate_data(self):
        """Load crate data for selected party"""
        try:
            if not self.party_var.get():
                return
                
            party_code = self.party_var.get().split(' - ')[0]
            crate_data = self.queries.get_crate_management_by_party(party_code)
            
            if crate_data:
                self.total_crates_var.set(str(crate_data.get('total_crates', 0)))
                self.crates_given_var.set(str(crate_data.get('crates_given', 0)))
                self.crates_received_var.set(str(crate_data.get('crates_received', 0)))
                self.crate_type_var.set(crate_data.get('crate_type', 'Standard'))
                self.calculate_remaining()
            else:
                self.clear_form()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load party crate data: {e}")
            
    def calculate_remaining(self):
        """Calculate and display remaining crates"""
        try:
            total = int(self.total_crates_var.get() or 0)
            given = int(self.crates_given_var.get() or 0)
            received = int(self.crates_received_var.get() or 0)
            
            remaining = given - received
            self.remaining_label.config(text=str(remaining))
            
            if remaining < 0:
                self.remaining_label.config(foreground='red', text=f"{remaining} (Excess)")
            elif remaining == 0:
                self.remaining_label.config(foreground='green', text="0 (Balanced)")
            else:
                self.remaining_label.config(foreground='blue', text=f"{remaining} (Pending)")
                
        except ValueError:
            self.remaining_label.config(text="Invalid", foreground='red')
            
    def save_crate_data(self):
        """Save crate management data"""
        try:
            if not self.party_var.get():
                messagebox.showerror("Error", "Please select a party")
                return
                
            party_code = self.party_var.get().split(' - ')[0]
            
            crate_data = {
                'party_cd': party_code,
                'total_crates': int(self.total_crates_var.get() or 0),
                'crates_given': int(self.crates_given_var.get() or 0),
                'crates_received': int(self.crates_received_var.get() or 0),
                'crate_type': self.crate_type_var.get()
            }
            
            if self.queries.save_crate_management(crate_data):
                messagebox.showinfo("Success", "Crate data saved successfully")
                self.load_crate_list()
                self.calculate_remaining()
                self.main_app.update_status(f"Crate data saved for {self.party_var.get()}")
            else:
                messagebox.showerror("Error", "Failed to save crate data")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for crate quantities")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save crate data: {e}")
            
    def on_crate_select(self, event):
        """Handle crate record selection"""
        try:
            selection = self.crate_tree.selection()
            if selection:
                item = self.crate_tree.item(selection[0])
                party_name = item['values'][0]
                
                parties = self.queries.get_all_parties()
                for party in parties:
                    if party['party_nm'] == party_name:
                        self.party_var.set(f"{party['party_cd']} - {party['party_nm']}")
                        self.load_party_crate_data()
                        break
                        
        except Exception as e:
            print(f"Error selecting crate record: {e}")
            
    def clear_form(self):
        """Clear the form"""
        self.total_crates_var.set('0')
        self.crates_given_var.set('0')
        self.crates_received_var.set('0')
        self.crate_type_var.set('Standard')
        self.remaining_label.config(text="0", foreground='blue')
    
    def import_crate_data(self):
        """Import crate data from DBF file"""
        try:
            from business.dbf_parser import DBFParser
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="Select CRATE.DBF file",
                filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            parser = DBFParser(file_path)
            records = parser.parse()
            
            if not records:
                messagebox.showerror("Error", "No records found in DBF file")
                return
            
            imported_count = 0
            for record in records:
                try:
                    party_code = record.get('PARTY_CD', '')
                    if party_code:
                        crate_data = {
                            'party_cd': party_code,
                            'total_crates': record.get('TOTAL_CRATES', 0),
                            'crates_given': record.get('CRATES_GIVEN', 0),
                            'crates_received': record.get('CRATES_RECEIVED', 0),
                            'crate_type': record.get('CRATE_TYPE', 'Standard')
                        }
                        
                        if self.queries.save_crate_management(crate_data):
                            imported_count += 1
                            
                except Exception as e:
                    print(f"Error importing record: {e}")
                    continue
            
            messagebox.showinfo("Success", f"Imported {imported_count} crate records")
            self.load_crate_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import crate data: {e}")
