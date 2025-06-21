"""
Print All Reports form - Comprehensive report printing interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.queries import DatabaseQueries

class PrintAllReportsForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Print All Reports")
        self.window.geometry("800x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        
    def setup_form(self):
        """Setup the print all reports form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_header_section(main_frame)
        self.create_reports_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_header_section(self, parent):
        """Create header section"""
        header_frame = ttk.LabelFrame(parent, text="Report Selection", padding=10)
        header_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header_frame, text="Select reports to print:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w')
        
    def create_reports_section(self, parent):
        """Create reports selection section"""
        reports_frame = ttk.LabelFrame(parent, text="Available Reports", padding=10)
        reports_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.reports_vars = {}
        
        reports = [
            ("Purchase Reports", "purchase_reports"),
            ("Sales Reports", "sales_reports"),
            ("Stock Report", "stock_report"),
            ("Ledger Reports", "ledger_reports"),
            ("Trial Balance", "trial_balance"),
            ("Party Statements", "party_statements"),
            ("Cash Book", "cashbook"),
            ("Bank Book", "bankbook"),
            ("Journal Entries", "journal"),
            ("Receipts", "receipts"),
            ("Stock Adjustments", "stock_adjustments")
        ]
        
        row = 0
        col = 0
        for report_name, report_key in reports:
            var = tk.BooleanVar()
            self.reports_vars[report_key] = var
            
            ttk.Checkbutton(reports_frame, text=report_name, 
                           variable=var).grid(row=row, column=col, sticky='w', padx=10, pady=5)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        ttk.Button(reports_frame, text="Select All", 
                  command=self.select_all_reports, 
                  style='Primary.TButton').grid(row=row+1, column=0, pady=10, sticky='w')
        
        ttk.Button(reports_frame, text="Clear All", 
                  command=self.clear_all_reports, 
                  style='Modern.TButton').grid(row=row+1, column=1, pady=10, sticky='w')
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Print Selected Reports", 
                  command=self.print_selected_reports, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Export All to PDF", 
                  command=self.export_all_to_pdf, 
                  style='Success.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Export All to Excel", 
                  command=self.export_all_to_excel, 
                  style='Warning.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def select_all_reports(self):
        """Select all reports"""
        for var in self.reports_vars.values():
            var.set(True)
    
    def clear_all_reports(self):
        """Clear all report selections"""
        for var in self.reports_vars.values():
            var.set(False)
    
    def print_selected_reports(self):
        """Print selected reports"""
        try:
            selected_reports = [key for key, var in self.reports_vars.items() if var.get()]
            
            if not selected_reports:
                messagebox.showwarning("Warning", "Please select at least one report to print")
                return
            
            print_window = tk.Toplevel(self.window)
            print_window.title("All Reports - Print Preview")
            print_window.geometry("900x700")
            
            text_widget = tk.Text(print_window, font=('Courier', 9))
            scrollbar = ttk.Scrollbar(print_window, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            scrollbar.pack(side='right', fill='y', pady=10)
            
            report_content = self.generate_combined_reports(selected_reports)
            text_widget.insert('1.0', report_content)
            text_widget.config(state='disabled')
            
            button_frame = ttk.Frame(print_window)
            button_frame.pack(fill='x', pady=5)
            
            ttk.Button(button_frame, text="Close", 
                      command=print_window.destroy).pack(side='right', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print reports: {e}")
    
    def export_all_to_pdf(self):
        """Export all selected reports to PDF"""
        try:
            selected_reports = [key for key, var in self.reports_vars.items() if var.get()]
            
            if not selected_reports:
                messagebox.showwarning("Warning", "Please select at least one report to export")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Report Type', 'Generated On', 'Status']
            data = []
            
            for report in selected_reports:
                data.append([report.replace('_', ' ').title(), 
                           datetime.now().strftime('%d/%m/%Y %H:%M:%S'), 
                           'Generated'])
            
            title = "All Business Reports"
            ExportUtils.export_to_pdf(data, headers, title, "all_reports")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def export_all_to_excel(self):
        """Export all selected reports to Excel"""
        try:
            selected_reports = [key for key, var in self.reports_vars.items() if var.get()]
            
            if not selected_reports:
                messagebox.showwarning("Warning", "Please select at least one report to export")
                return
            
            from business.export_utils import ExportUtils
            
            headers = ['Report Type', 'Generated On', 'Status']
            data = []
            
            for report in selected_reports:
                data.append([report.replace('_', ' ').title(), 
                           datetime.now().strftime('%d/%m/%Y %H:%M:%S'), 
                           'Generated'])
            
            ExportUtils.export_to_excel(data, headers, "all_reports", "All Business Reports")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {e}")
    
    def generate_combined_reports(self, selected_reports):
        """Generate combined reports content"""
        content = []
        content.append("COMPREHENSIVE BUSINESS REPORTS")
        content.append("=" * 80)
        content.append("")
        content.append(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        content.append("")
        
        for report in selected_reports:
            content.append(f"\n{report.replace('_', ' ').upper()}")
            content.append("-" * 50)
            content.append("Sample data would be displayed here...")
            content.append("")
        
        return '\n'.join(content)
