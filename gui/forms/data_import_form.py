"""
Data Import Form for Visual FoxPro files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from database.foxpro_import import FoxProImporter

class DataImportForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.importer = FoxProImporter(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Import Visual FoxPro Data")
        self.window.geometry("800x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        
    def setup_form(self):
        """Setup the import form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        title_label = ttk.Label(main_frame, text="Import Data from Visual FoxPro", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        self.create_path_selection(main_frame)
        self.create_import_options(main_frame)
        self.create_progress_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_path_selection(self, parent):
        """Create path selection section"""
        path_frame = ttk.LabelFrame(parent, text="Select Visual FoxPro Data Directory", padding=10)
        path_frame.pack(fill='x', pady=(0, 10))
        
        self.path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.path_var, width=60).pack(side='left', fill='x', expand=True)
        
        ttk.Button(path_frame, text="Browse", 
                  command=self.browse_directory,
                  style='Primary.TButton').pack(side='right', padx=(10, 0))
        
    def create_import_options(self, parent):
        """Create import options section"""
        options_frame = ttk.LabelFrame(parent, text="Import Options", padding=10)
        options_frame.pack(fill='x', pady=(0, 10))
        
        self.import_parties_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Import Parties (PARMST.DBF)", 
                       variable=self.import_parties_var).pack(anchor='w', pady=2)
        
        self.import_items_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Import Items (IT.DBF)", 
                       variable=self.import_items_var).pack(anchor='w', pady=2)
        
        self.import_purchases_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Import Purchases (PURC.DBF)", 
                       variable=self.import_purchases_var).pack(anchor='w', pady=2)
        
        self.import_sales_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Import Sales (SALE.DBF)", 
                       variable=self.import_sales_var).pack(anchor='w', pady=2)
        
    def create_progress_section(self, parent):
        """Create progress section"""
        progress_frame = ttk.LabelFrame(parent, text="Import Progress", padding=10)
        progress_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.progress_var = tk.StringVar(value="Ready to import...")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(anchor='w', pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=5)
        
        self.log_text = tk.Text(progress_frame, height=15, wrap='word')
        scrollbar = ttk.Scrollbar(progress_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Start Import", 
                  command=self.start_import,
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear Log", 
                  command=self.clear_log,
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy,
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def browse_directory(self):
        """Browse for Visual FoxPro directory"""
        directory = filedialog.askdirectory(title="Select Visual FoxPro Data Directory")
        if directory:
            self.path_var.set(directory)
            
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.window.update()
        
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete('1.0', tk.END)
        
    def start_import(self):
        """Start the import process"""
        try:
            if not self.path_var.get():
                messagebox.showerror("Error", "Please select a directory")
                return
            
            if not os.path.exists(self.path_var.get()):
                messagebox.showerror("Error", "Selected directory does not exist")
                return
            
            self.progress_var.set("Starting import...")
            self.progress_bar.start()
            self.log_message("Starting Visual FoxPro data import...")
            
            results = {}
            
            if self.import_parties_var.get():
                self.progress_var.set("Importing parties...")
                self.log_message("Importing parties from PARMST.DBF...")
                count = self.importer.import_parties(self.path_var.get())
                results['parties'] = count
                self.log_message(f"Imported {count} parties")
            
            if self.import_items_var.get():
                self.progress_var.set("Importing items...")
                self.log_message("Importing items from IT.DBF...")
                count = self.importer.import_items(self.path_var.get())
                results['items'] = count
                self.log_message(f"Imported {count} items")
            
            if self.import_purchases_var.get():
                self.progress_var.set("Importing purchases...")
                self.log_message("Importing purchases from PURC.DBF...")
                count = self.importer.import_purchases(self.path_var.get())
                results['purchases'] = count
                self.log_message(f"Imported {count} purchases")
            
            if self.import_sales_var.get():
                self.progress_var.set("Importing sales...")
                self.log_message("Importing sales from SALE.DBF...")
                count = self.importer.import_sales(self.path_var.get())
                results['sales'] = count
                self.log_message(f"Imported {count} sales")
            
            self.progress_bar.stop()
            self.progress_var.set("Import completed!")
            
            total_imported = sum(results.values())
            self.log_message(f"\nImport completed successfully!")
            self.log_message(f"Total records imported: {total_imported}")
            
            messagebox.showinfo("Success", f"Import completed!\nTotal records imported: {total_imported}")
            self.main_app.update_status(f"Data import completed: {total_imported} records")
            
        except Exception as e:
            self.progress_bar.stop()
            self.progress_var.set("Import failed!")
            self.log_message(f"Error during import: {e}")
            messagebox.showerror("Error", f"Import failed: {e}")
            import traceback
            traceback.print_exc()
