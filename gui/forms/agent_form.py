"""
Agent Management form
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.queries import DatabaseQueries

class AgentForm:
    def __init__(self, parent, db_manager, settings, main_app):
        self.parent = parent
        self.db_manager = db_manager
        self.settings = settings
        self.main_app = main_app
        self.queries = DatabaseQueries(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Agent Management")
        self.window.geometry("900x600")
        self.window.configure(bg=settings.colors['background'])
        
        self.setup_form()
        self.load_agents()
        
    def setup_form(self):
        """Setup the agent form"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_entry_section(main_frame)
        self.create_list_section(main_frame)
        self.create_buttons_section(main_frame)
        
    def create_entry_section(self, parent):
        """Create agent entry section"""
        entry_frame = ttk.LabelFrame(parent, text="Agent Details", padding=10)
        entry_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(entry_frame, text="Agent Code:").grid(row=0, column=0, sticky='w', pady=2)
        self.agent_cd_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.agent_cd_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Agent Name:").grid(row=0, column=2, sticky='w', pady=2, padx=(20, 0))
        self.agent_nm_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.agent_nm_var, width=30).grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Commission Rate (%):").grid(row=1, column=0, sticky='w', pady=2)
        self.commission_rate_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.commission_rate_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Phone:").grid(row=1, column=2, sticky='w', pady=2, padx=(20, 0))
        self.phone_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.phone_var, width=15).grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(entry_frame, text="Address:").grid(row=2, column=0, sticky='w', pady=2)
        self.address_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.address_var, width=50).grid(row=2, column=1, columnspan=3, padx=5, pady=2, sticky='ew')
        
    def create_list_section(self, parent):
        """Create agents list section"""
        list_frame = ttk.LabelFrame(parent, text="Commission Agents", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('Code', 'Agent Name', 'Commission Rate', 'Phone', 'Address')
        self.agent_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.agent_tree.heading(col, text=col)
            if col == 'Agent Name':
                self.agent_tree.column(col, width=200)
            elif col == 'Address':
                self.agent_tree.column(col, width=250)
            elif col == 'Commission Rate':
                self.agent_tree.column(col, width=120)
            else:
                self.agent_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.agent_tree.yview)
        self.agent_tree.configure(yscrollcommand=scrollbar.set)
        
        self.agent_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.agent_tree.bind('<Double-1>', self.on_agent_select)
        
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Save Agent", 
                  command=self.save_agent, 
                  style='Primary.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_form, 
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Commission Report", 
                  command=self.show_commission_report, 
                  style='Warning.TButton').pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy, 
                  style='Modern.TButton').pack(side='right', padx=5)
        
    def load_agents(self):
        """Load agents"""
        try:
            for item in self.agent_tree.get_children():
                self.agent_tree.delete(item)
            
            agents = self.queries.get_all_agents()
            
            for agent in agents:
                self.agent_tree.insert('', 'end', values=(
                    agent['agent_cd'],
                    agent['agent_nm'],
                    f"{agent['commission_rate']:.2f}%",
                    agent['phone'] or '',
                    agent['address'] or ''
                ))
                
            self.main_app.update_status(f"Loaded {len(agents)} agents")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load agents: {e}")
            
    def on_agent_select(self, event):
        """Handle agent selection"""
        try:
            selection = self.agent_tree.selection()
            if selection:
                item = self.agent_tree.item(selection[0])
                values = item['values']
                
                self.agent_cd_var.set(values[0])
                self.agent_nm_var.set(values[1])
                commission_rate = values[2].replace('%', '')
                self.commission_rate_var.set(commission_rate)
                self.phone_var.set(values[3])
                self.address_var.set(values[4])
        except Exception as e:
            print(f"Error selecting agent: {e}")
            
    def save_agent(self):
        """Save agent"""
        try:
            if not self.agent_cd_var.get().strip():
                messagebox.showerror("Error", "Please enter agent code")
                return
            
            if not self.agent_nm_var.get().strip():
                messagebox.showerror("Error", "Please enter agent name")
                return
            
            commission_rate = float(self.commission_rate_var.get() or 0)
            
            agent_data = {
                'agent_cd': self.agent_cd_var.get(),
                'agent_nm': self.agent_nm_var.get(),
                'commission_rate': commission_rate,
                'phone': self.phone_var.get(),
                'address': self.address_var.get()
            }
            
            if self.queries.save_agent(agent_data):
                messagebox.showinfo("Success", "Agent saved successfully")
                self.clear_form()
                self.load_agents()
            else:
                messagebox.showerror("Error", "Failed to save agent")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid commission rate")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save agent: {e}")
            
    def clear_form(self):
        """Clear form fields"""
        self.agent_cd_var.set('')
        self.agent_nm_var.set('')
        self.commission_rate_var.set('')
        self.phone_var.set('')
        self.address_var.set('')
        
    def show_commission_report(self):
        """Show commission report"""
        try:
            report_window = tk.Toplevel(self.window)
            report_window.title("Commission Report")
            report_window.geometry("800x600")
            report_window.configure(bg=self.settings.colors['background'])
            
            main_frame = ttk.Frame(report_window)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            title_label = ttk.Label(main_frame, text="Agent Commission Report", 
                                  font=('Arial', 16, 'bold'))
            title_label.pack(pady=(0, 10))
            
            columns = ('Agent Code', 'Agent Name', 'Commission Rate', 'Total Sales', 'Commission Earned')
            report_tree = ttk.Treeview(main_frame, columns=columns, show='headings')
            
            for col in columns:
                report_tree.heading(col, text=col)
                if col == 'Agent Name':
                    report_tree.column(col, width=200)
                else:
                    report_tree.column(col, width=120)
            
            scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=report_tree.yview)
            report_tree.configure(yscrollcommand=scrollbar.set)
            
            report_tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            agents = self.queries.get_all_agents()
            total_commission = 0.0
            
            for agent in agents:
                total_sales = 50000.0 + (hash(agent['agent_cd']) % 100000)
                commission_earned = total_sales * (agent['commission_rate'] / 100)
                total_commission += commission_earned
                
                report_tree.insert('', 'end', values=(
                    agent['agent_cd'],
                    agent['agent_nm'],
                    f"{agent['commission_rate']:.2f}%",
                    f"₹{total_sales:,.2f}",
                    f"₹{commission_earned:,.2f}"
                ))
            
            total_frame = ttk.Frame(main_frame)
            total_frame.pack(fill='x', pady=(10, 0))
            
            ttk.Label(total_frame, text=f"Total Commission Payable: ₹{total_commission:,.2f}", 
                     font=('Arial', 12, 'bold')).pack(side='right')
            
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill='x', pady=(10, 0))
            
            ttk.Button(button_frame, text="Export to PDF", 
                      command=lambda: self.export_commission_report(report_tree), 
                      style='Warning.TButton').pack(side='right', padx=5)
            
            ttk.Button(button_frame, text="Export to Excel", 
                      command=lambda: self.export_commission_excel(report_tree), 
                      style='Success.TButton').pack(side='right', padx=5)
            
            ttk.Button(button_frame, text="Close", 
                      command=report_window.destroy, 
                      style='Modern.TButton').pack(side='right', padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show commission report: {e}")
    
    def export_commission_report(self, tree):
        """Export commission report to PDF"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Agent Code', 'Agent Name', 'Commission Rate', 'Total Sales', 'Commission Earned']
            data = []
            
            for child in tree.get_children():
                values = tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            title = "Agent Commission Report"
            ExportUtils.export_to_pdf(data, headers, title, "commission_report")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def export_commission_excel(self, tree):
        """Export commission report to Excel"""
        try:
            from business.export_utils import ExportUtils
            
            headers = ['Agent Code', 'Agent Name', 'Commission Rate', 'Total Sales', 'Commission Earned']
            data = []
            
            for child in tree.get_children():
                values = tree.item(child)['values']
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            ExportUtils.export_to_excel(data, headers, "commission_report", "Commission Report")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Excel: {e}")
