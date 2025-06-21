"""
Debit Notes form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries

class DebitNotesForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Debit Notes")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_debit_notes()
        
    def setup_form(self):
        """Setup the debit notes form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create debit note entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Debit Note Entry", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Bill No:").grid(row=0, column=0, sticky='w', pady=2)
        self.bill_no_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.bill_no_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Date:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(entry_frame, textvariable=self.date_var, width=15).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Party:").grid(row=1, column=0, sticky='w', pady=2)
        self.party_var = tk.StringVar()
        self.party_combo = ttk.Combobox(entry_frame, textvariable=self.party_var, width=30)
        self.party_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Truck No:").grid(row=1, column=3, sticky='w', pady=2, padx=(20, 0))
        self.truck_no_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.truck_no_var, width=15).grid(row=1, column=4, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Item:").grid(row=2, column=0, sticky='w', pady=2)
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(entry_frame, textvariable=self.item_var, width=30)
        self.item_combo.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Quantity:").grid(row=3, column=0, sticky='w', pady=2)
        self.qty_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.qty_var, width=15).grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Rate:").grid(row=3, column=2, sticky='w', pady=2, padx=(20, 0))
        self.rate_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.rate_var, width=15).grid(row=3, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Amount:").grid(row=3, column=4, sticky='w', pady=2, padx=(20, 0))
        self.amount_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.amount_var, width=15).grid(row=3, column=5, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Particulars:").grid(row=4, column=0, sticky='w', pady=2)
        self.particulars_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.particulars_var, width=30).grid(row=4, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Description:").grid(row=5, column=0, sticky='w', pady=2)
        self.description_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.description_var, width=50).grid(row=5, column=1, columnspan=5, padx=5, pady=2, sticky='ew')
        
        self.load_parties()
        self.load_items()
        
    def create_list_section(self, parent):
        """Create debit notes list section"""
        list_frame = ttk.LabelFrame(parent, text="Debit Notes", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Bill No', 'Date', 'Party', 'Item', 'Qty', 'Rate', 'Amount', 'Particulars')
        self.debit_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.debit_tree.heading(col, text=col)
            if col in ['Party', 'Item']:
                self.debit_tree.column(col, width=150)
            elif col == 'Particulars':
                self.debit_tree.column(col, width=200)
            else:
                self.debit_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.debit_tree.yview)
        self.debit_tree.configure(yscrollcommand=scrollbar.set)
        
        self.debit_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Debit Note", 
                  command=self.save_debit_note, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_form, 
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Print Note", 
                  command=self.print_note, 
                  style='Warning.TButton').pack(side='right', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_parties(self):
        """Load parties for dropdown"""
        try:
            parties = self.queries.get_all_parties()
            party_list = [f"{p['party_cd']} - {p['party_nm']}" for p in parties]
            self.party_combo['values'] = party_list
        except Exception as e:
            print(f"Error loading parties: {e}")
            
    def load_items(self):
        """Load items for dropdown"""
        try:
            items = self.queries.get_all_items()
            item_list = [f"{i['it_cd']} - {i['it_nm']}" for i in items]
            self.item_combo['values'] = item_list
        except Exception as e:
            print(f"Error loading items: {e}")
            
    def load_debit_notes(self):
        """Load debit notes"""
        try:
            for item in self.debit_tree.get_children():
                self.debit_tree.delete(item)
            
            notes = self.queries.get_all_debit_notes()
            
            for note in notes:
                party_name = note.get('party_nm', '') or ''
                item_name = note.get('it_nm', '') or ''
                
                self.debit_tree.insert('', 'end', values=(
                    note['bill_no'],
                    note['bill_date'],
                    party_name,
                    item_name,
                    f"{note['qty']:.2f}" if note['qty'] else '',
                    f"₹{note['rate']:.2f}" if note['rate'] else '',
                    f"₹{note['amount']:.2f}",
                    note['particulars'] or ''
                ))
                
            self.main_app.update_status(f"Loaded {len(notes)} debit notes")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load debit notes: {e}")
            
    def save_debit_note(self):
        """Save debit note"""
        try:
            if not self.bill_no_var.get().strip():
                messagebox.showerror("Error", "Please enter bill number")
                return
            
            if not self.party_var.get():
                messagebox.showerror("Error", "Please select a party")
                return
            
            if not self.amount_var.get().strip():
                messagebox.showerror("Error", "Please enter amount")
                return
            
            amount = float(self.amount_var.get())
            party_code = self.party_var.get().split(' - ')[0]
            item_code = ''
            if self.item_var.get():
                item_code = self.item_var.get().split(' - ')[0]
            
            note_data = {
                'bill_no': int(self.bill_no_var.get()),
                'bill_date': datetime.strptime(self.date_var.get(), '%d/%m/%Y').date(),
                'party_cd': party_code,
                'truck_no': self.truck_no_var.get(),
                'particulars': self.particulars_var.get(),
                'description': self.description_var.get(),
                'amount': amount,
                'tot_amt': amount,
                'it_cd': item_code,
                'qty': float(self.qty_var.get() or 0),
                'rate': float(self.rate_var.get() or 0)
            }
            
            if self.queries.save_debit_note(note_data):
                messagebox.showinfo("Success", "Debit note saved successfully")
                self.clear_form()
                self.load_debit_notes()
            else:
                messagebox.showerror("Error", "Failed to save debit note")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid bill number and amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save debit note: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.bill_no_var.set('')
        self.date_var.set(datetime.now().strftime('%d/%m/%Y'))
        self.party_var.set('')
        self.truck_no_var.set('')
        self.item_var.set('')
        self.qty_var.set('')
        self.rate_var.set('')
        self.amount_var.set('')
        self.particulars_var.set('')
        self.description_var.set('')
        
    def print_note(self):
        """Print debit note with preview and export options"""
        try:
            selection = self.debit_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a debit note to print")
                return
            
            item = self.debit_tree.item(selection[0])
            values = item['values']
            
            print_window = tk.Toplevel(self.window)
            print_window.title("Debit Note - Print Preview")
            print_window.geometry("700x600")
            print_window.configure(bg=self.settings.colors['background'])
            
            preview_frame = ttk.Frame(print_window)
            preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            report_text = self.generate_debit_note_text(values)
            
            text_widget = tk.Text(preview_frame, font=('Courier', 10), wrap='word')
            text_widget.pack(fill='both', expand=True, pady=(0, 10))
            text_widget.insert('1.0', report_text)
            text_widget.config(state='disabled')
            
            button_frame = ttk.Frame(preview_frame)
            button_frame.pack(fill='x')
            
            ttk.Button(button_frame, text="Export to PDF", 
                      command=lambda: self.export_debit_note_pdf(values),
                      style='Warning.TButton').pack(side='left', padx=5)
            
            ttk.Button(button_frame, text="Export to Excel", 
                      command=lambda: self.export_debit_note_excel(values),
                      style='Success.TButton').pack(side='left', padx=5)
            
            ttk.Button(button_frame, text="Close", 
                      command=print_window.destroy,
                      style='Modern.TButton').pack(side='right', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print debit note: {e}")
    
    def generate_debit_note_text(self, values):
        """Generate debit note text for printing"""
        lines = []
        lines.append("=" * 70)
        lines.append("DEBIT NOTE".center(70))
        lines.append("=" * 70)
        lines.append(f"Bill No: {values[0]}")
        lines.append(f"Date: {values[1]}")
        lines.append(f"Party: {values[2]}")
        lines.append("-" * 70)
        lines.append(f"Item: {values[3]}")
        lines.append(f"Quantity: {values[4]}")
        lines.append(f"Rate: {values[5]}")
        lines.append(f"Amount: {values[6]}")
        lines.append("-" * 70)
        lines.append(f"Particulars: {values[7]}")
        lines.append("=" * 70)
        return '\n'.join(lines)
    
    def export_debit_note_pdf(self, values):
        """Export debit note to PDF"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Field', 'Value']
            data = [
                ['Bill No', values[0]],
                ['Date', values[1]],
                ['Party', values[2]],
                ['Item', values[3]],
                ['Quantity', values[4]],
                ['Rate', values[5]],
                ['Amount', values[6]],
                ['Particulars', values[7]]
            ]
            
            title = f"Debit Note #{values[0]}"
            ExportUtils.export_to_pdf(data, headers, title, f"debit_note_{values[0]}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def export_debit_note_excel(self, values):
        """Export debit note to Excel"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Field', 'Value']
            data = [
                ['Bill No', values[0]],
                ['Date', values[1]],
                ['Party', values[2]],
                ['Item', values[3]],
                ['Quantity', values[4]],
                ['Rate', values[5]],
                ['Amount', values[6]],
                ['Particulars', values[7]]
            ]
            
            ExportUtils.export_to_excel(data, headers, f"debit_note_{values[0]}", f"Debit Note {values[0]}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {e}")
