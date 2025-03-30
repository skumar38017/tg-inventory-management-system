import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import platform
import logging
import random
import string
import json
import os

logger = logging.getLogger(__name__)

class ToEventWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs - To Event")

        # Track wrap state
        self.is_wrapped = False
        self.original_column_widths = []
        
        # Database file
        self.db_file = "inventory_data.json"
        
        # Initialize database
        self.initialize_db()
        
        # Hide parent window (optional)
        self.parent.withdraw()
        
        # Setup the window
        self.setup_ui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Focus on this window
        self.window.focus_set()
        
        # Maximize window
        self.maximize_window()
        
        # Set initial state
        self.set_fields_readonly(False)
        
        # Generate and set WorkID automatically
        self.generate_work_id()
        
        # Load initial data
        self.load_submitted_forms()
        
        logger.info("To Event window opened successfully")

    def initialize_db(self):
        """Initialize the JSON database file if it doesn't exist"""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump([], f)

    def save_to_db(self, data):
        """Save data to the JSON database"""
        try:
            with open(self.db_file, 'r') as f:
                records = json.load(f)
            
            # Check if this work_id already exists
            existing_index = None
            for i, record in enumerate(records):
                if record['work_id'] == data['work_id']:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # Update existing record
                records[existing_index] = data
            else:
                # Add new record
                records.append(data)
            
            with open(self.db_file, 'w') as f:
                json.dump(records, f, indent=4)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save to database: {str(e)}")
            return False

    def load_from_db(self, work_id=None):
        """Load data from the JSON database"""
        try:
            with open(self.db_file, 'r') as f:
                records = json.load(f)
            
            if work_id:
                for record in records:
                    if record['work_id'] == work_id:
                        return record
                return None
            else:
                return records
        except Exception as e:
            logger.error(f"Failed to load from database: {str(e)}")
            return None

    def generate_work_id(self):
        """Generate a random WorkID in format PRJ followed by 5 digits"""
        prefix = "PRJ"
        digits = ''.join(random.choices(string.digits, k=5))
        work_id = f"{prefix}{digits}"
        self.work_id.config(state='normal')
        self.work_id.delete(0, tk.END)
        self.work_id.insert(0, work_id)
        self.work_id.config(state='readonly')
        return work_id

    def set_fields_readonly(self, readonly):
        """Set all fields to readonly or editable"""
        state = 'readonly' if readonly else 'normal'
        
        # Main fields
        self.employee_name.config(state=state)
        self.location.config(state=state)
        self.client_name.config(state=state)
        self.setup_date.config(state=state)
        self.project_name.config(state=state)
        self.event_date.config(state=state)
        self.work_id.config(state='readonly')  # Always readonly
        self.project_id.config(state='normal')  # Project ID is editable for fetching
        
        # Table entries
        for row in self.table_entries:
            for entry in row:
                entry.config(state=state)

    def maximize_window(self):
        try:
            self.window.state('zoomed')
        except tk.TclError:
            try:
                if platform.system() == 'Linux':
                    self.window.attributes('-zoomed', True)
                else:
                    self.window.attributes('-fullscreen', True)
            except:
                self.window.geometry("{0}x{1}+0+0".format(
                    self.window.winfo_screenwidth(),
                    self.window.winfo_screenheight()
                ))

    def setup_ui(self):
        """Set up all UI elements"""
        # Header section
        clock_frame = tk.Frame(self.window)
        clock_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=0)
        clock_frame.grid_columnconfigure(0, weight=1)
        clock_frame.grid_columnconfigure(1, weight=0)
        clock_frame.grid_columnconfigure(2, weight=1)

        self.clock_label = tk.Label(clock_frame, font=('Helvetica', 8))
        self.clock_label.grid(row=0, column=1, sticky='n', pady=(0,0))
        self.update_clock()

        # Company info
        company_frame = tk.Frame(self.window)
        company_frame.grid(row=1, column=0, columnspan=2, sticky="e", padx=10, pady=0)
        company_frame.grid_columnconfigure(0, weight=1)

        company_info = """Tagglabs Experiential Pvt. Ltd.
        Sector 49, Gurugram, Haryana 122018
        201, Second Floor, Eros City Square Mall
        Eros City Square
        098214 43358"""

        company_label = tk.Label(company_frame,
                               text=company_info,
                               font=('Helvetica', 7),
                               justify=tk.RIGHT)
        company_label.grid(row=0, column=1, sticky='ne', pady=(0,0))

        # Title section
        title_frame = tk.Frame(self.window)
        title_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        tk.Label(title_frame, 
               text="Tagglabs Experiential Pvt. Ltd",
               font=('Helvetica', 14, 'bold')).pack()
        
        tk.Label(title_frame, 
               text="INVENTORY LIST",
               font=('Helvetica', 12, 'bold')).pack()

        # Information fields
        info_frame = tk.Frame(self.window)
        info_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # First row - Work ID and buttons
        tk.Label(info_frame, text="Project ID (Search):", font=('Helvetica', 9)).grid(row=0, column=0, sticky='e', padx=2)
        self.project_id = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.project_id.grid(row=0, column=1, sticky='w', padx=2)
                
        self.fetch_btn = tk.Button(info_frame, text="Fetch", command=self.fetch_record,
                                 font=('Helvetica', 9, 'bold'))
        self.fetch_btn.grid(row=0, column=2, padx=5)
        
        self.edit_btn = tk.Button(info_frame, text="Edit", command=self.edit_record,
                                font=('Helvetica', 9, 'bold'), state=tk.NORMAL)
        self.edit_btn.grid(row=0, column=3, padx=5)
        
        self.update_btn = tk.Button(info_frame, text="Update", command=self.update_record,
                                  font=('Helvetica', 9, 'bold'), state=tk.DISABLED)
        self.update_btn.grid(row=0, column=4, padx=5)

        # Second row - all fields (added Work ID at the end)
        tk.Label(info_frame, text="Employee Name:", font=('Helvetica', 9)).grid(row=1, column=0, sticky='e', padx=2)
        self.employee_name = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.employee_name.grid(row=1, column=1, sticky='w', padx=2)
        
        tk.Label(info_frame, text="Location:", font=('Helvetica', 9)).grid(row=1, column=2, sticky='e', padx=2)
        self.location = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.location.grid(row=1, column=3, sticky='w', padx=2)
        
        tk.Label(info_frame, text="Client Name:", font=('Helvetica', 9)).grid(row=1, column=4, sticky='e', padx=2)
        self.client_name = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.client_name.grid(row=1, column=5, sticky='w', padx=2)
        
        tk.Label(info_frame, text="Setup Date:", font=('Helvetica', 9)).grid(row=1, column=6, sticky='e', padx=2)
        self.setup_date = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.setup_date.grid(row=1, column=7, sticky='w', padx=2)
        
        tk.Label(info_frame, text="Project Name:", font=('Helvetica', 9)).grid(row=1, column=8, sticky='e', padx=2)
        self.project_name = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.project_name.grid(row=1, column=9, sticky='w', padx=2)
        
        tk.Label(info_frame, text="Event Date:", font=('Helvetica', 9)).grid(row=1, column=10, sticky='e', padx=2)
        self.event_date = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.event_date.grid(row=1, column=11, sticky='w', padx=2)
        
        # Current Work ID display
        tk.Label(info_frame, text="Current Work ID:", font=('Helvetica', 9)).grid(row=1, column=12, sticky='e', padx=2)
        self.work_id = tk.Entry(info_frame, font=('Helvetica', 9), width=15, state='readonly')
        self.work_id.grid(row=1, column=13, sticky='w', padx=2)

        # Separator line
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # Inventory table
        self.table_frame = tk.Frame(self.window)
        self.table_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.table_frame)
        self.v_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.pack(side="bottom", fill="x")

        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.yview_moveto(0)

        # Table headers
        self.headers = [
            "Zone/Activity", "Sr. No.", "Inventory", "Description/Specifications",
            "Quantity", "Comments", "Total", "Units", 
            "Per Unit Power Consumption (Watt/H)", "Total Power Consumption (Watt)",
            "Status (purchased/not purchased)", "POC"
        ]

        self.original_column_widths = [20 if col not in [4,6,7,8,9] else 15 for col in range(len(self.headers))]
        
        for col, header in enumerate(self.headers):
            tk.Label(self.scrollable_frame, text=header, font=('Helvetica', 9, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")

        # Create entry fields
        self.table_entries = []
        for row in range(1, 6):  # 5 empty rows
            row_entries = []
            for col in range(len(self.headers)):
                entry = tk.Entry(self.scrollable_frame, font=('Helvetica', 9), 
                               width=self.original_column_widths[col])
                entry.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                row_entries.append(entry)
            self.table_entries.append(row_entries)

        # Create Notebook for tabs
        self.tab_control = ttk.Notebook(self.window)
        self.tab_control.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5,0))

        # Tab 1: Submitted Forms
        self.submitted_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.submitted_tab, text="Submitted Forms")
        self.setup_submitted_tab()

        # Tab 2: Search Results
        self.search_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.search_tab, text="Search Results")
        self.setup_search_tab()

        # Bottom buttons
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.wrap_btn = tk.Button(button_frame, text="Wrap", command=self.toggle_wrap,
                                font=('Helvetica', 10, 'bold'))
        self.wrap_btn.pack(side=tk.LEFT, padx=5)

        remove_row_btn = tk.Button(button_frame, text="Remove Row", command=self.remove_table_row,
                                 font=('Helvetica', 10, 'bold'))
        remove_row_btn.pack(side=tk.LEFT, padx=5)

        add_row_btn = tk.Button(button_frame, text="Add Row", command=self.add_table_row,
                              font=('Helvetica', 10, 'bold'))
        add_row_btn.pack(side=tk.LEFT, padx=5)

        submit_btn = tk.Button(button_frame, text="Submit", command=self.submit_form,
                             font=('Helvetica', 10, 'bold'))
        submit_btn.pack(side=tk.LEFT, padx=5)

        return_button = tk.Button(button_frame, 
                                text="Return to Main", 
                                command=self.on_close,
                                font=('Helvetica', 10, 'bold'),
                                width=15)
        return_button.pack(side=tk.RIGHT, padx=5)

        # Grid configuration
        self.window.grid_rowconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=0)
        self.window.grid_rowconfigure(2, weight=0)
        self.window.grid_rowconfigure(3, weight=0)
        self.window.grid_rowconfigure(4, weight=0)
        self.window.grid_rowconfigure(5, weight=1)
        self.window.grid_rowconfigure(6, weight=1)
        self.window.grid_rowconfigure(7, weight=0)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

    def setup_submitted_tab(self):
        """Setup the tab for submitted forms"""
        frame = tk.Frame(self.submitted_tab)
        frame.pack(fill="both", expand=True)

        # Treeview for submitted forms
        self.submitted_tree = ttk.Treeview(frame, height=10,
                                         columns=("WorkID", "Employee", "Location", "ProjectName", "Client", "SetupDate", "EventDate"),
                                         show="headings")
        
        # Configure columns
        self.submitted_tree.heading("WorkID", text="Work ID")
        self.submitted_tree.heading("Employee", text="Employee")
        self.submitted_tree.heading("Location", text="Location")
        self.submitted_tree.heading("ProjectName", text="Project Name")
        self.submitted_tree.heading("Client", text="Client Name")
        self.submitted_tree.heading("SetupDate", text="Setup Date")
        self.submitted_tree.heading("EventDate", text="Event Date")
        
        self.submitted_tree.column("WorkID", width=100)
        self.submitted_tree.column("Employee", width=150)
        self.submitted_tree.column("Location", width=100)
        self.submitted_tree.column("ProjectName", width=100)
        self.submitted_tree.column("Client", width=100)
        self.submitted_tree.column("SetupDate", width=100)
        self.submitted_tree.column("EventDate", width=100)

        # Scrollbars
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.submitted_tree.yview)
        self.submitted_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=y_scroll.set)

        # Grid layout
        self.submitted_tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

        # Double-click to load project
        self.submitted_tree.bind("<Double-1>", self.load_submitted_project)

    def setup_search_tab(self):
        """Setup the tab for search results"""
        frame = tk.Frame(self.search_tab)
        frame.pack(fill="both", expand=True)

        # Treeview for search results
        self.search_tree = ttk.Treeview(frame, height=10,
                                      columns=("WorkID", "ProjectName", "Employee", "Location", "Client", "SetupDate", "EventDate"),
                                      show="headings")
        
        # Configure columns
        self.search_tree.heading("WorkID", text="Work ID")
        self.search_tree.heading("ProjectName", text="Project Name")
        self.search_tree.heading("Employee", text="Employee")
        self.search_tree.heading("Location", text="Location")
        self.search_tree.heading("Client", text="Client")
        self.search_tree.heading("SetupDate", text="Setup Date")
        self.search_tree.heading("EventDate", text="Event Date")
        
        self.search_tree.column("WorkID", width=100)
        self.search_tree.column("ProjectName", width=100)
        self.search_tree.column("Employee", width=150)
        self.search_tree.column("Location", width=100)
        self.search_tree.column("Client", width=150)
        self.search_tree.column("SetupDate", width=100)
        self.search_tree.column("EventDate", width=100)

        # Scrollbars
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=y_scroll.set)

        # Grid layout
        self.search_tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

        # Double-click to load project
        self.search_tree.bind("<Double-1>", self.load_search_result)

    def load_submitted_forms(self):
        """Load all submitted forms into the submitted tab"""
        # Clear existing items
        for item in self.submitted_tree.get_children():
            self.submitted_tree.delete(item)
        
        records = self.load_from_db()
        
        if not records:
            return
        
        for record in records:
            self.submitted_tree.insert("", "end", values=(
                record['work_id'],
                record['employee_name'],
                record['location'],
                record['project_name'],
                record['client_name'],
                record['setup_date'],
                record['event_date']
            ))

    def load_submitted_project(self, event):
        """Load project from submitted tab when double-clicked"""
        selected = self.submitted_tree.selection()
        if selected:
            item = self.submitted_tree.item(selected)
            work_id = item['values'][0]
            self.load_project_data(work_id)

    def fetch_record(self):
        """Search records by Work ID and display in Search Results tab"""
        work_id = self.project_id.get().strip()  # Using project_id field to input work_id for search
        if not work_id:
            messagebox.showwarning("Warning", "Please enter a Work ID to search")
            return
            
        record = self.load_from_db(work_id)
        
        if not record:
            messagebox.showinfo("Info", f"No records found for Work ID: {work_id}")
            return
                
        # Clear existing items in search tab
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
            
        # Populate search tab with the found record
        self.search_tree.insert("", "end", values=(
            record['work_id'],
            record['project_name'],
            record['employee_name'],
            record['location'],
            record['client_name'],
            record['setup_date'],
            record['event_date']
        ))
        
        # Switch to search results tab
        self.tab_control.select(self.search_tab)

    def load_search_result(self, event):
        """Load project from search results when double-clicked"""
        selected = self.search_tree.selection()
        if selected:
            item = self.search_tree.item(selected)
            work_id = item['values'][0]
            self.load_project_data(work_id)

    def load_project_data(self, work_id):
        """Load project data into the form"""
        record = self.load_from_db(work_id)
        if not record:
            messagebox.showerror("Error", f"Record with Work ID {work_id} not found")
            return
        
        # Populate form fields
        self.work_id.config(state='normal')
        self.work_id.delete(0, tk.END)
        self.work_id.insert(0, record['work_id'])
        self.work_id.config(state='readonly')
        
        self.employee_name.delete(0, tk.END)
        self.employee_name.insert(0, record['employee_name'])
        
        self.location.delete(0, tk.END)
        self.location.insert(0, record['location'])
        
        self.client_name.delete(0, tk.END)
        self.client_name.insert(0, record['client_name'])
        
        self.setup_date.delete(0, tk.END)
        self.setup_date.insert(0, record['setup_date'])
        
        self.project_name.delete(0, tk.END)
        self.project_name.insert(0, record['project_name'])
        
        self.event_date.delete(0, tk.END)
        self.event_date.insert(0, record['event_date'])
        
        # Clear existing table entries
        for row in self.table_entries:
            for entry in row:
                entry.delete(0, tk.END)
        
        # Add enough rows for all inventory items
        while len(self.table_entries) < len(record['inventory_items']):
            self.add_table_row()
        
        # Fill in the inventory items
        for i, item in enumerate(record['inventory_items']):
            if i >= len(self.table_entries):
                break
                
            row = self.table_entries[i]
            row[0].insert(0, item['zone_activity'])
            row[1].insert(0, item['sr_no'])
            row[2].insert(0, item['inventory'])
            row[3].insert(0, item['description'])
            row[4].insert(0, item['quantity'])
            row[5].insert(0, item['comments'])
            row[6].insert(0, item['total'])
            row[7].insert(0, item['units'])
            row[8].insert(0, item['power_per_unit'])
            row[9].insert(0, item['total_power'])
            row[10].insert(0, item['status'])
            row[11].insert(0, item['poc'])
        
        # Switch back to form view
        self.tab_control.select(0)
        
        # Set fields to readonly initially
        self.set_fields_readonly(True)
        self.edit_btn.config(state=tk.NORMAL)
        self.update_btn.config(state=tk.DISABLED)

    def edit_record(self):
        """Enable editing of the record"""
        if not self.work_id.get():
            messagebox.showwarning("Warning", "No record loaded to edit")
            return
            
        self.set_fields_readonly(False)
        self.edit_btn.config(state=tk.DISABLED)
        self.update_btn.config(state=tk.NORMAL)
        logger.info("Editing record")

    def update_record(self):
        """Update the record in database"""
        try:
            work_id = self.work_id.get()
            if not work_id:
                messagebox.showwarning("Warning", "Work ID is required for update")
                return
                
            # Prepare the data to be saved
            data = {
                'work_id': work_id,  # Work ID never changes
                'employee_name': self.employee_name.get(),
                'location': self.location.get(),
                'client_name': self.client_name.get(),
                'setup_date': self.setup_date.get(),
                'project_name': self.project_name.get(),
                'event_date': self.event_date.get(),
                'inventory_items': []
            }
            
            for row in self.table_entries:
                item = {
                    'zone_activity': row[0].get(),
                    'sr_no': row[1].get(),
                    'inventory': row[2].get(),
                    'description': row[3].get(),
                    'quantity': row[4].get(),
                    'comments': row[5].get(),
                    'total': row[6].get(),
                    'units': row[7].get(),
                    'power_per_unit': row[8].get(),
                    'total_power': row[9].get(),
                    'status': row[10].get(),
                    'poc': row[11].get()
                }
                data['inventory_items'].append(item)
            
            if not self.save_to_db(data):
                raise Exception("Failed to save to database")
            
            messagebox.showinfo("Success", "Record updated successfully")
            logger.info(f"Record updated: {data}")
            
            # Set fields back to readonly
            self.set_fields_readonly(True)
            self.edit_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)
            
            # Refresh submitted forms tab
            self.load_submitted_forms()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update record: {str(e)}")
            logger.error(f"Update failed: {str(e)}")

    def toggle_wrap(self):
        """Toggle between wrapped and original column sizes"""
        if not self.is_wrapped:
            self.adjust_columns()
            self.wrap_btn.config(text="Unwrap")
            self.is_wrapped = True
        else:
            self.reset_columns()
            self.wrap_btn.config(text="Wrap")
            self.is_wrapped = False

    def adjust_columns(self):
        """Adjust column widths based on content"""
        col_widths = [len(header) for header in self.headers]
        
        for row in self.table_entries:
            for col, entry in enumerate(row):
                content = entry.get()
                if content:
                    col_widths[col] = max(col_widths[col], len(content))
        
        for col, width in enumerate(col_widths):
            adjusted_width = min(width + 5, 50)
            self.scrollable_frame.grid_columnconfigure(col, minsize=adjusted_width * 8)
            
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.xview_moveto(0)

    def reset_columns(self):
        """Reset columns to their original widths"""
        for col, width in enumerate(self.original_column_widths):
            self.scrollable_frame.grid_columnconfigure(col, minsize=width * 10)
            
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.xview_moveto(0)

    def add_table_row(self):
        """Add a new row to the table"""
        current_rows = len(self.table_entries)
        
        row_entries = []
        for col in range(len(self.headers)):
            entry = tk.Entry(self.scrollable_frame, font=('Helvetica', 9), 
                           width=self.original_column_widths[col])
            entry.grid(row=current_rows+1, column=col, sticky="ew", padx=2, pady=2)
            row_entries.append(entry)
        self.table_entries.append(row_entries)
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def remove_table_row(self):
        """Remove the last row from the table"""
        if len(self.table_entries) <= 1:
            messagebox.showwarning("Warning", "Cannot remove the last row")
            return
            
        last_row = self.table_entries.pop()
        for entry in last_row:
            entry.destroy()
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def submit_form(self):
        """Handle form submission"""
        if not self.employee_name.get() or not self.client_name.get():
            messagebox.showwarning("Warning", "Please fill in all required fields")
            return
            
        data = {
            'work_id': self.work_id.get(),  # Work ID never changes
            'employee_name': self.employee_name.get(),
            'location': self.location.get(),
            'client_name': self.client_name.get(),
            'setup_date': self.setup_date.get(),
            'project_name': self.project_name.get(),
            'event_date': self.event_date.get(),
            'inventory_items': []
        }
        
        for row in self.table_entries:
            item = {
                'zone_activity': row[0].get(),
                'sr_no': row[1].get(),
                'inventory': row[2].get(),
                'description': row[3].get(),
                'quantity': row[4].get(),
                'comments': row[5].get(),
                'total': row[6].get(),
                'units': row[7].get(),
                'power_per_unit': row[8].get(),
                'total_power': row[9].get(),
                'status': row[10].get(),
                'poc': row[11].get()
            }
            data['inventory_items'].append(item)
        
        if not self.save_to_db(data):
            messagebox.showerror("Error", "Failed to save record")
            return
        
        messagebox.showinfo("Success", "Form submitted successfully")
        logger.info(f"Form submitted: {data}")
        
        # Clear form and generate new WorkID
        self.clear_form()
        self.generate_work_id()
        
        # Refresh submitted forms tab
        self.load_submitted_forms()
        self.tab_control.select(self.submitted_tab)

    def clear_form(self):
        """Clear all form fields"""
        self.project_id.delete(0, tk.END)
        self.employee_name.delete(0, tk.END)
        self.location.delete(0, tk.END)
        self.client_name.delete(0, tk.END)
        self.setup_date.delete(0, tk.END)
        self.project_name.delete(0, tk.END)
        self.event_date.delete(0, tk.END)
        
        # Clear table entries
        for row in self.table_entries:
            for entry in row:
                entry.delete(0, tk.END)

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing To Event window")
        self.window.destroy()
        self.parent.deiconify()