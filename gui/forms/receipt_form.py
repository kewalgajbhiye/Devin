"""
Receipt Management form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries

class ReceiptForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Receipt Management")
        self.window.geometry("1000x700")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_receipts()
        
    def setup_form(self):
        """Setup the receipt form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create receipt entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Receipt Entry", padding=10)
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
        
        ttk.Label(entry_frame, text="Amount:").grid(row=2, column=0, sticky='w', pady=2)
        self.amount_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.amount_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Payment Mode:").grid(row=2, column=2, sticky='w', pady=2, padx=(20, 0))
        self.payment_mode_var = tk.StringVar(value='CASH')
        payment_modes = ['CASH', 'CHEQUE', 'RTGS', 'NEFT', 'UPI', 'CARD']
        self.payment_combo = ttk.Combobox(entry_frame, textvariable=self.payment_mode_var, values=payment_modes, width=15)
        self.payment_combo.grid(row=2, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Bank Name:").grid(row=3, column=0, sticky='w', pady=2)
        self.bank_name_var = tk.StringVar()
        bank_names = ['STATE BANK OF INDIA', 'HDFC BANK', 'ICICI BANK', 'AXIS BANK', 'PUNJAB NATIONAL BANK']
        self.bank_combo = ttk.Combobox(entry_frame, textvariable=self.bank_name_var, values=bank_names, width=25)
        self.bank_combo.grid(row=3, column=1, columnspan=2, padx=5, pady=2, sticky='ew')
        
        ttk.Label(entry_frame, text="Cheque No:").grid(row=3, column=3, sticky='w', pady=2, padx=(20, 0))
        self.cheque_no_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.cheque_no_var, width=15).grid(row=3, column=4, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Particulars:").grid(row=4, column=0, sticky='w', pady=2)
        self.particulars_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.particulars_var, width=40).grid(row=4, column=1, columnspan=4, padx=5, pady=2, sticky='ew')
        
        self.load_parties()
        
    def create_list_section(self, parent):
        """Create receipts list section"""
        list_frame = ttk.LabelFrame(parent, text="Receipt Records", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Bill No', 'Date', 'Party', 'Amount', 'Payment Mode', 'Bank', 'Cheque No', 'Particulars')
        self.receipt_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.receipt_tree.heading(col, text=col)
            if col == 'Amount':
                self.receipt_tree.column(col, width=100)
            elif col in ['Particulars']:
                self.receipt_tree.column(col, width=150)
            elif col in ['Bank', 'Party']:
                self.receipt_tree.column(col, width=120)
            else:
                self.receipt_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.receipt_tree.yview)
        self.receipt_tree.configure(yscrollcommand=scrollbar.set)
        
        self.receipt_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Receipt", 
                  command=self.save_receipt, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_form, 
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Print Receipt", 
                  command=self.print_receipt, 
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
            
    def load_receipts(self):
        """Load receipts"""
        try:
            for item in self.receipt_tree.get_children():
                self.receipt_tree.delete(item)
            
            receipts = self.queries.get_all_receipts()
            
            for receipt in receipts:
                party_name = receipt.get('party_nm', '') or ''
                
                self.receipt_tree.insert('', 'end', values=(
                    receipt['bill_no'],
                    receipt['bill_date'],
                    party_name,
                    f"₹{receipt['amount']:.2f}",
                    receipt['payment_mode'] or '',
                    receipt['bank_name'] or '',
                    receipt['cheque_no'] or '',
                    receipt['particulars'] or ''
                ))
                
            self.main_app.update_status(f"Loaded {len(receipts)} receipts")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load receipts: {e}")
            
    def save_receipt(self):
        """Save receipt"""
        try:
            if not self.bill_no_var.get().strip():
                messagebox.showerror("Error", "Please enter bill number")
                return
            
            if not self.amount_var.get().strip():
                messagebox.showerror("Error", "Please enter amount")
                return
            
            if not self.party_var.get():
                messagebox.showerror("Error", "Please select a party")
                return
            
            amount = float(self.amount_var.get())
            party_code = self.party_var.get().split(' - ')[0]
            
            receipt_data = {
                'bill_no': int(self.bill_no_var.get()),
                'bill_date': datetime.strptime(self.date_var.get(), '%d/%m/%Y').date(),
                'party_cd': party_code,
                'amount': amount,
                'particulars': self.particulars_var.get(),
                'payment_mode': self.payment_mode_var.get(),
                'cheque_no': self.cheque_no_var.get(),
                'bank_name': self.bank_name_var.get()
            }
            
            if self.queries.save_receipt(receipt_data):
                messagebox.showinfo("Success", "Receipt saved successfully")
                self.clear_form()
                self.load_receipts()
            else:
                messagebox.showerror("Error", "Failed to save receipt")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid bill number and amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save receipt: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.bill_no_var.set('')
        self.date_var.set(datetime.now().strftime('%d/%m/%Y'))
        self.party_var.set('')
        self.amount_var.set('')
        self.particulars_var.set('')
        self.payment_mode_var.set('CASH')
        self.bank_name_var.set('')
        self.cheque_no_var.set('')
        
    def print_receipt(self):
        """Print receipt with preview and export options"""
        try:
            selection = self.receipt_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a receipt to print")
                return
            
            item = self.receipt_tree.item(selection[0])
            receipt_data = item['values']
            
            print_window = tk.Toplevel(self.window)
            print_window.title("Receipt - Print Preview")
            print_window.geometry("600x500")
            print_window.configure(bg=self.settings.colors['background'])
            
            preview_frame = ttk.Frame(print_window)
            preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            receipt_text = self.generate_receipt_text(receipt_data)
            
            text_widget = tk.Text(preview_frame, font=('Courier', 10), wrap='word')
            text_widget.pack(fill='both', expand=True, pady=(0, 10))
            text_widget.insert('1.0', receipt_text)
            text_widget.config(state='disabled')
            
            button_frame = ttk.Frame(preview_frame)
            button_frame.pack(fill='x')
            
            ttk.Button(button_frame, text="Export to PDF", 
                      command=lambda: self.export_receipt_pdf(receipt_data), 
                      style='Warning.TButton').pack(side='left', padx=5)
            
            ttk.Button(button_frame, text="Export to Excel", 
                      command=lambda: self.export_receipt_excel(receipt_data), 
                      style='Success.TButton').pack(side='left', padx=5)
            
            ttk.Button(button_frame, text="Close", 
                      command=print_window.destroy, 
                      style='Modern.TButton').pack(side='right', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print receipt: {e}")
    
    def generate_receipt_text(self, receipt_data):
        """Generate receipt text for printing"""
        lines = []
        lines.append("=" * 60)
        lines.append("PAYMENT RECEIPT".center(60))
        lines.append("=" * 60)
        lines.append(f"Receipt No: {receipt_data[0]}")
        lines.append(f"Date: {receipt_data[1]}")
        lines.append(f"Party: {receipt_data[2]}")
        lines.append("-" * 60)
        lines.append(f"Amount Received: {receipt_data[3]}")
        lines.append(f"Payment Mode: {receipt_data[4]}")
        if receipt_data[5]:
            lines.append(f"Bank: {receipt_data[5]}")
        if receipt_data[6]:
            lines.append(f"Cheque No: {receipt_data[6]}")
        lines.append(f"Particulars: {receipt_data[7]}")
        lines.append("-" * 60)
        lines.append(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("=" * 60)
        return '\n'.join(lines)
    
    def export_receipt_pdf(self, receipt_data):
        """Export receipt to PDF"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Field', 'Value']
            data = [
                ['Receipt No', receipt_data[0]],
                ['Date', receipt_data[1]],
                ['Party', receipt_data[2]],
                ['Amount', receipt_data[3]],
                ['Payment Mode', receipt_data[4]],
                ['Bank', receipt_data[5] or 'N/A'],
                ['Cheque No', receipt_data[6] or 'N/A'],
                ['Particulars', receipt_data[7] or 'N/A']
            ]
            
            title = f"Payment Receipt #{receipt_data[0]}"
            ExportUtils.export_to_pdf(data, headers, title, f"receipt_{receipt_data[0]}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def export_receipt_excel(self, receipt_data):
        """Export receipt to Excel"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Field', 'Value']
            data = [
                ['Receipt No', receipt_data[0]],
                ['Date', receipt_data[1]],
                ['Party', receipt_data[2]],
                ['Amount', receipt_data[3]],
                ['Payment Mode', receipt_data[4]],
                ['Bank', receipt_data[5] or 'N/A'],
                ['Cheque No', receipt_data[6] or 'N/A'],
                ['Particulars', receipt_data[7] or 'N/A']
            ]
            
            ExportUtils.export_to_excel(data, headers, f"receipt_{receipt_data[0]}", f"Receipt {receipt_data[0]}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {e}")
