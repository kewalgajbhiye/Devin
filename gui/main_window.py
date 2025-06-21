"""
Main application window with modern Tkinter UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkFont
from datetime import datetime, date
from database.models import DatabaseManager
from database.queries import DatabaseQueries
from business.purchase import PurchaseManager
from business.reports import ReportGenerator
from gui.forms.purchase_form import PurchaseEntryForm
from gui.forms.party_form import PartyForm
from gui.forms.item_form import ItemForm
from gui.forms.sales_form import SalesEntryForm
from gui.forms.stock_report import StockReportForm
from gui.forms.ledger_reports import LedgerReportsForm
from gui.forms.trial_balance import TrialBalanceForm
from gui.forms.purchase_reports import PurchaseReportsForm
from gui.forms.party_statements import PartyStatementsForm
from gui.forms.sales_reports import SalesReportsForm
from gui.components.dashboard_cards import DashboardCards

class ModernBusinessApp:
    def __init__(self, db_manager, settings):
        self.db_manager = db_manager
        self.settings = settings
        self.queries = DatabaseQueries(db_manager)
        self.purchase_manager = PurchaseManager(db_manager)
        self.report_generator = ReportGenerator(db_manager)
        
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.create_main_interface()
        
    def setup_window(self):
        """Setup main window properties"""
        self.root.title(self.settings.app_name)
        self.root.geometry(f"{self.settings.window_width}x{self.settings.window_height}")
        self.root.configure(bg=self.settings.colors['background'])
        
        self.root.minsize(800, 600)
        
        try:
            self.root.state('zoomed')
        except tk.TclError:
            pass
    
    def setup_styles(self):
        """Setup modern color scheme and styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        colors = self.settings.colors
        
        self.style.configure('Card.TFrame', 
                           background=colors['card'], 
                           relief='raised', 
                           borderwidth=2)
        
        self.style.configure('Header.TLabel', 
                           font=('Arial', 16, 'bold'), 
                           background=colors['primary'], 
                           foreground='white',
                           padding=10)
        
        self.style.configure('Title.TLabel',
                           font=('Arial', 14, 'bold'),
                           background=colors['card'],
                           foreground=colors['text'])
        
        self.style.configure('Modern.TButton', 
                           font=('Arial', 10, 'bold'),
                           padding=8)
        
        self.style.configure('Primary.TButton',
                           background=colors['primary'],
                           foreground='white',
                           font=('Arial', 10, 'bold'),
                           padding=8)
        
        self.style.configure('Success.TButton',
                           background=colors['success'],
                           foreground='white',
                           font=('Arial', 10, 'bold'),
                           padding=8)
        
        self.style.configure('Warning.TButton',
                           background=colors['warning'],
                           foreground=colors['text'],
                           font=('Arial', 10, 'bold'),
                           padding=8)
        
        self.style.configure('Status.TLabel',
                           background=colors['background'],
                           foreground=colors['muted'],
                           font=('Arial', 9))
    
    def create_main_interface(self):
        """Create main dashboard interface"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_header(main_frame)
        self.create_dashboard(main_frame)
        self.create_status_bar()
        
    def create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        company_details = self.settings.company_details
        
        title_label = ttk.Label(header_frame, 
                               text=company_details['name'],
                               style='Header.TLabel')
        title_label.pack(pady=5)
        
        subtitle_label = ttk.Label(header_frame,
                                 text=company_details['business_type'],
                                 font=('Arial', 12),
                                 background=self.settings.colors['card'],
                                 foreground=self.settings.colors['text'])
        subtitle_label.pack()
        
        address_label = ttk.Label(header_frame,
                                text=f"{company_details['address1']}, {company_details['city']}",
                                font=('Arial', 10),
                                background=self.settings.colors['card'],
                                foreground=self.settings.colors['muted'])
        address_label.pack()
        
        contact_label = ttk.Label(header_frame,
                                text=f"Umesh: {company_details['phone_umesh']}, Harish: {company_details['phone_harish']}",
                                font=('Arial', 10),
                                background=self.settings.colors['card'],
                                foreground=self.settings.colors['muted'])
        contact_label.pack(pady=(0, 5))
    
    def create_dashboard(self, parent):
        """Create dashboard with cards"""
        dashboard_frame = ttk.Frame(parent)
        dashboard_frame.pack(fill='both', expand=True)
        
        self.dashboard_cards = DashboardCards(dashboard_frame, self.settings, self)
        self.dashboard_cards.create_cards()
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.status_bar = ttk.Label(self.root, 
                                   textvariable=self.status_var,
                                   style='Status.TLabel',
                                   relief='sunken')
        self.status_bar.pack(side='bottom', fill='x')
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
        self.root.update_idletasks()
    
    def open_purchase_form(self):
        """Open purchase entry form"""
        try:
            self.update_status("Opening purchase entry form...")
            PurchaseEntryForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open purchase form: {e}")
            self.update_status("Error opening purchase form")
    
    def open_party_form(self):
        """Open party management form"""
        try:
            self.update_status("Opening party management form...")
            PartyForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open party form: {e}")
            self.update_status("Error opening party form")
    
    def open_item_form(self):
        """Open item management form"""
        try:
            self.update_status("Opening item management form...")
            ItemForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open item form: {e}")
            self.update_status("Error opening item form")
    
    def print_purchase_bill(self):
        """Print purchase bill with user-friendly selection"""
        try:
            self.update_status("Opening purchase bill selection...")
            from gui.forms.print_purchase_bill_form import PrintPurchaseBillForm
            PrintPurchaseBillForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open print purchase bill form: {e}")
            self.update_status("Error opening print purchase bill form")
    
    def print_sales_bill(self):
        """Print sales bill with user-friendly selection"""
        try:
            self.update_status("Opening sales bill selection...")
            from gui.forms.print_sales_bill_form import PrintSalesBillForm
            PrintSalesBillForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open print sales bill form: {e}")
            self.update_status("Error opening print sales bill form")
    
    def open_sales_form(self):
        """Open sales entry form"""
        try:
            self.update_status("Opening sales entry form...")
            SalesEntryForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open sales form: {e}")
            self.update_status("Error opening sales form")
    
    def show_sales_reports(self):
        """Show sales reports"""
        try:
            self.update_status("Opening sales reports...")
            SalesReportsForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open sales reports: {e}")
            self.update_status("Error opening sales reports")
    
    def show_stock_report(self):
        """Show stock report"""
        try:
            self.update_status("Opening stock report...")
            StockReportForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open stock report: {e}")
            self.update_status("Error opening stock report")
    
    def show_ledger_reports(self):
        """Show ledger reports"""
        try:
            self.update_status("Opening ledger reports...")
            LedgerReportsForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ledger reports: {e}")
            self.update_status("Error opening ledger reports")
    
    def show_trial_balance(self):
        """Show trial balance"""
        try:
            self.update_status("Opening trial balance...")
            TrialBalanceForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open trial balance: {e}")
            self.update_status("Error opening trial balance")
    
    def show_purchase_reports(self):
        """Show purchase reports"""
        try:
            self.update_status("Opening purchase reports...")
            PurchaseReportsForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open purchase reports: {e}")
            self.update_status("Error opening purchase reports")
    
    def show_party_statements(self):
        """Show party statements"""
        try:
            self.update_status("Opening party statements...")
            PartyStatementsForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open party statements: {e}")
            self.update_status("Error opening party statements")

    def open_cashbook_form(self):
        """Open cash book form"""
        try:
            self.update_status("Opening cash book form...")
            from gui.forms.cashbook_form import CashBookForm
            CashBookForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open cash book form: {e}")
            self.update_status("Error opening cash book form")
    
    def open_bankbook_form(self):
        """Open bank book form"""
        try:
            self.update_status("Opening bank book form...")
            from gui.forms.bankbook_form import BankBookForm
            BankBookForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open bank book form: {e}")
            self.update_status("Error opening bank book form")
    
    def open_journal_form(self):
        """Open journal form"""
        try:
            self.update_status("Opening journal form...")
            from gui.forms.journal_form import JournalForm
            JournalForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open journal form: {e}")
            self.update_status("Error opening journal form")
    
    def open_receipt_form(self):
        """Open receipt form"""
        try:
            self.update_status("Opening receipt form...")
            from gui.forms.receipt_form import ReceiptForm
            ReceiptForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open receipt form: {e}")
            self.update_status("Error opening receipt form")
    
    def open_stock_adjustment_form(self):
        """Open stock adjustment form"""
        try:
            self.update_status("Opening stock adjustment form...")
            from gui.forms.stock_adjustment_form import StockAdjustmentForm
            StockAdjustmentForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open stock adjustment form: {e}")
            self.update_status("Error opening stock adjustment form")
    
    def open_lot_management_form(self):
        """Open lot management form"""
        try:
            self.update_status("Opening lot management form...")
            from gui.forms.lot_management_form import LotManagementForm
            LotManagementForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open lot management form: {e}")
            self.update_status("Error opening lot management form")
    
    def print_sales_entry(self):
        """Print sales entry with user-friendly selection"""
        try:
            self.update_status("Opening sales entry selection...")
            from gui.forms.print_sales_entry_form import PrintSalesEntryForm
            PrintSalesEntryForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open print sales entry form: {e}")
            self.update_status("Error opening print sales entry form")
    
    def open_print_all_reports_form(self):
        """Open print all reports form"""
        try:
            self.update_status("Opening print all reports form...")
            from gui.forms.print_all_reports_form import PrintAllReportsForm
            PrintAllReportsForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open print all reports form: {e}")
            self.update_status("Error opening print all reports form")
    
    def open_transport_form(self):
        """Open transport form"""
        try:
            self.update_status("Opening transport form...")
            from gui.forms.transport_form import TransportForm
            TransportForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open transport form: {e}")
            self.update_status("Error opening transport form")
    
    def open_agent_form(self):
        """Open agent form"""
        try:
            self.update_status("Opening agent form...")
            from gui.forms.agent_form import AgentForm
            AgentForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open agent form: {e}")
            self.update_status("Error opening agent form")
    
    def open_credit_notes_form(self):
        """Open credit notes form"""
        try:
            self.update_status("Opening credit notes form...")
            from gui.forms.credit_notes_form import CreditNotesForm
            CreditNotesForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open credit notes form: {e}")
            self.update_status("Error opening credit notes form")
    
    def open_debit_notes_form(self):
        """Open debit notes form"""
        try:
            self.update_status("Opening debit notes form...")
            from gui.forms.debit_notes_form import DebitNotesForm
            DebitNotesForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open debit notes form: {e}")
            self.update_status("Error opening debit notes form")

    def show_about(self):
        """Show about dialog"""
        about_text = f"""
{self.settings.app_name}
Version {self.settings.version}

Modern business management software for vegetable wholesale operations.

Developed for:
{self.settings.company_details['name']}
{self.settings.company_details['business_type']}

© 2024 - Modernized Desktop Application
        """
        messagebox.showinfo("About", about_text.strip())
    
    def print_purchase_entry(self):
        """Open print purchase entry form"""
        try:
            from gui.forms.print_purchase_entry_form import PrintPurchaseEntryForm
            PrintPurchaseEntryForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open print purchase entry form: {e}")
            print(f"Error opening print purchase entry form: {e}")
            import traceback
            traceback.print_exc()
    
    def open_salepatti_form(self):
        """Open SALEPATTI enhanced sales entry form"""
        try:
            from gui.forms.salepatti_form import SalepattiForm
            SalepattiForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open SALEPATTI form: {e}")
            print(f"Error opening SALEPATTI form: {e}")
            import traceback
            traceback.print_exc()
    
    def open_crate_management_form(self):
        """Open crate management form"""
        try:
            from gui.forms.crate_management_form import CrateManagementForm
            CrateManagementForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open crate management form: {e}")
            print(f"Error opening crate management form: {e}")
            import traceback
            traceback.print_exc()
    
    def open_data_import_form(self):
        """Open data import form"""
        try:
            from gui.forms.data_import_form import DataImportForm
            DataImportForm(self.root, self.db_manager, self.settings, self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open data import form: {e}")
            print(f"Error opening data import form: {e}")
            import traceback
            traceback.print_exc()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_status("Application started successfully")
        self.root.mainloop()
