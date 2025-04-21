# frontend/app/to_event.py

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import platform
import logging
import random
import string
import json
import os
from tkcalendar import Calendar, DateEntry
from utils.field_validators import StatusEnum
from widgets.inventory_combobox import InventoryComboBox
from api_request.to_event_inventory_request import (
    create_to_event_inventory_list, 
    load_submitted_project_from_db,
    update_submitted_project_in_db,
    search_project_details_by_id
)

logger = logging.getLogger(__name__)

class ToEventWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs - To Event")

        # Track wrap state
        self.is_wrapped = False
        self.original_column_widths = []

        # Get status options from StatusEnum
        self.status_options = [status.value for status in StatusEnum]
        
        # Database file
        self.db_file = "inventory_data.json"

        # Initialize inventory combo box data
        self.inventory_combo_data = []
        
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
 
    def save_to_db(self, data, work_id=None):
        """Save data to the database via API"""
        try:
            work_id = data['work_id']

            # First check if project exists - handle 404 as non-error case
            try:
                existing_records = search_project_details_by_id(work_id)
                if existing_records:
                    # Update existing recordsave_to_db
                    if not update_submitted_project_in_db(work_id, data):
                        raise Exception("Failed to update record via API")
                    return True
            except Exception as e:
                logger.warning(f"Project check failed, attempting create: {str(e)}")

            # Create new record
            api_response = create_to_event_inventory_list(data)
            logger.info(f"New record created via API: {api_response}")
            return True

        except Exception as e:
            logger.error(f"Failed to save to database: {str(e)}")
            return False

    def load_from_db(self, work_id=None):
        """Load data from API only"""
        try:
            if work_id:
                # Load single record by work_id
                records = search_project_details_by_id(work_id)
                return records[0] if records else None
            else:
                # Load all records sorted by updated_at in descending order
                records = load_submitted_project_from_db()
                if records:
                    # Sort by updated_at in descending order
                    return sorted(records, key=lambda x: x.get('updated_at', ''), reverse=True)
                return []

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
            for col, entry in enumerate(row):
                if col == 12:  # RecQty column (index 12)
                    entry.config(state='readonly')  # Always readonly
                elif col == 2:  # Inventory column (InventoryComboBox)
                    entry.config(state='readonly' if readonly else 'normal')
                else:
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
               text="To Create Event Inventory List",
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

        # Add new entry button on the same row (column 5)
        self.add_btn = tk.Button(info_frame, text="New Entry", command=self.new_button_click,
                                font=('Helvetica', 9, 'bold'))
        self.add_btn.grid(row=0, column=5, padx=5)

        # Add clear button on the same row (column 6)
        self.clear_btn = tk.Button(info_frame, text="Clear", command=self.clear_form,
                                font=('Helvetica', 9, 'bold'))
        self.clear_btn.grid(row=0, column=6, padx=5)

        # Add refresh button on the same row (column 7)
        self.refresh_btn = tk.Button(info_frame, text="Refresh", command=self.refresh_data,
                                   font=('Helvetica', 9, 'bold'))
        self.refresh_btn.grid(row=0, column=7, padx=5)

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
        self.setup_date = DateEntry(
            info_frame, 
            font=('Helvetica', 9), 
            width=15,
            date_pattern='yyyy-mm-dd',  # Changed format
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        self.setup_date.grid(row=1, column=7, sticky='w', padx=2)


        tk.Label(info_frame, text="Project Name:", font=('Helvetica', 9)).grid(row=1, column=8, sticky='e', padx=2)
        self.project_name = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.project_name.grid(row=1, column=9, sticky='w', padx=2)

        tk.Label(info_frame, text="Event Date:", font=('Helvetica', 9)).grid(row=1, column=10, sticky='e', padx=2)
        self.event_date = DateEntry(info_frame, 
                                font=('Helvetica', 9), 
                                width=15,
                                date_pattern='yyyy-mm-dd',
                                background='darkblue',
                                foreground='white',
                                borderwidth=2)
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
            "Zone/Activity", "Sr. No.", "Inventory", "Description",
            "Quantity", "Comments", "Total", "Units", "Per Unit Power (W)",
            "Total Power (W)", "Status", "POC", "RecQty"
        ]

        self.original_column_widths = [20 if col not in [4,6,7,8,9] else 15 for col in range(len(self.headers))]
        
        for col, header in enumerate(self.headers):
            tk.Label(self.scrollable_frame, text=header, font=('Helvetica', 9, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")

        # Create entry fields
        self.table_entries = []
        for row in range(1, 1):  # 2 empty rows
            row_entries = []
            for col in range(len(self.headers)):
                if col == 2:  # Inventory column - use InventoryComboBox
                    combo_frame = tk.Frame(self.scrollable_frame)
                    combo_frame.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                    
                    combo = InventoryComboBox(combo_frame)
                    combo.pack(fill=tk.X, expand=True)
                    
                    # Bind selection to update related fields
                    combo.bind('<<ComboboxSelected>>', 
                            lambda e, r=row_entries: self._update_inventory_fields(r, e))
                    row_entries.append(combo)
                elif col == 10:  # Status column
                    # Create Combobox for Status
                    status_var = tk.StringVar()
                    combo = ttk.Combobox(
                        self.scrollable_frame,
                        textvariable=status_var,
                        values=self.status_options,
                        state="state",
                        font=('Helvetica', 9)
                    )
                    combo.set(self.status_options[0])  # Set default status
                    combo.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                    row_entries.append(combo)
                else:
                    # Regular Entry for other columns
                    entry = tk.Entry(self.scrollable_frame, 
                                font=('Helvetica', 9), 
                                width=self.original_column_widths[col])
                    if col == 12:  # RecQty column (index 12) RecQty is readonly
                        entry.config(state='readonly')
                    entry.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                    row_entries.append(entry)
            self.table_entries.append(row_entries)

        # Create Notebook for tabs
        self.tab_control = ttk.Notebook(self.window)
        self.tab_control.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5,0))

        # Tab 1: Submitted Projects
        self.submitted_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.submitted_tab, text="Submitted Projects")
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
        self.add_table_row() 

    def _update_inventory_fields(self, row_entries, event):
        """Update related fields when an inventory item is selected"""
        # Get the combobox widget that triggered the event
        combo_box = event.widget
        
        # Get the selected item data
        selected_item = combo_box.get_selected_item()
        if selected_item:
            # Update all relevant fields from the selected inventory item
            if len(row_entries) > 1:  # Ensure we have at least the sno field
                # Update sno field (column 1)
                row_entries[1].delete(0, tk.END)
                row_entries[1].insert(0, str(selected_item.get('sno', '')))
                
                # Update description field (column 3) if it exists
                if len(row_entries) > 3:
                    row_entries[3].delete(0, tk.END)
                    row_entries[3].insert(0, str(selected_item.get('description', '')))

    def new_button_click(self):
        """Handle New Entry button click - clears the form and generates new Work ID"""
        self.clear_form()
        self.generate_work_id()
        self.set_fields_readonly(False)
        messagebox.showinfo("New Entry", "Ready to create a new entry")

    def setup_submitted_tab(self):
        """Setup the tab for submitted projects"""
        frame = tk.Frame(self.submitted_tab)
        frame.pack(fill="both", expand=True)

        # Treeview for submitted projects
        self.submitted_tree = ttk.Treeview(frame, height=10,
                                         columns=("WorkID", "Employee", "Location", "ProjectName", 
                                                 "Client", "SetupDate", "EventDate", "LastUpdated"),
                                         show="headings")
        
        # Configure columns
        self.submitted_tree.heading("WorkID", text="Work ID")
        self.submitted_tree.heading("Employee", text="Employee")
        self.submitted_tree.heading("Location", text="Location")
        self.submitted_tree.heading("ProjectName", text="Project Name")
        self.submitted_tree.heading("Client", text="Client Name")
        self.submitted_tree.heading("SetupDate", text="Setup Date")
        self.submitted_tree.heading("EventDate", text="Event Date")
        self.submitted_tree.heading("LastUpdated", text="Last Updated")
        
        self.submitted_tree.column("WorkID", width=100)
        self.submitted_tree.column("Employee", width=150)
        self.submitted_tree.column("Location", width=100)
        self.submitted_tree.column("ProjectName", width=150)
        self.submitted_tree.column("Client", width=150)
        self.submitted_tree.column("SetupDate", width=100)
        self.submitted_tree.column("EventDate", width=100)
        self.submitted_tree.column("LastUpdated", width=150)

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
                                      columns=("WorkID", "ProjectName", "Employee", "Location", 
                                              "Client", "SetupDate", "EventDate", "LastUpdated"),
                                      show="headings")
        
        # Configure columns
        self.search_tree.heading("WorkID", text="Work ID")
        self.search_tree.heading("ProjectName", text="Project Name")
        self.search_tree.heading("Employee", text="Employee")
        self.search_tree.heading("Location", text="Location")
        self.search_tree.heading("Client", text="Client")
        self.search_tree.heading("SetupDate", text="Setup Date")
        self.search_tree.heading("EventDate", text="Event Date")
        self.search_tree.heading("LastUpdated", text="Last Updated")
        
        self.search_tree.column("WorkID", width=100)
        self.search_tree.column("ProjectName", width=150)
        self.search_tree.column("Employee", width=150)
        self.search_tree.column("Location", width=100)
        self.search_tree.column("Client", width=150)
        self.search_tree.column("SetupDate", width=100)
        self.search_tree.column("EventDate", width=100)
        self.search_tree.column("LastUpdated", width=150)

        # Scrollbars
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=y_scroll.set)

        # Grid layout
        self.search_tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

        # Double-click to load project
        self.search_tree.bind("<Double-1>", self.load_search_result)

    def load_submitted_forms(self):
        """Load all submitted forms into the submitted tab sorted by updated_at"""
        # Clear existing items
        for item in self.submitted_tree.get_children():
            self.submitted_tree.delete(item)
        
        records = self.load_from_db()
        
        if not records:
            return
        
        for record in records:
            # Format the updated_at timestamp for display
            updated_at = record.get('updated_at', '')
            if updated_at:
                try:
                    # Convert to datetime object and format
                    dt = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")
                except:
                    formatted_date = updated_at
            else:
                formatted_date = 'Not available'
            
            self.submitted_tree.insert("", "end", values=(
                record['work_id'],
                record['employee_name'],
                record['location'],
                record['project_name'],
                record['client_name'],
                record['setup_date'],
                record['event_date'],
                formatted_date  # Make sure this is included
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
        work_id = self.project_id.get().strip()
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
            
        # Format the updated_at timestamp for display
        updated_at = record.get('updated_at', '')
        if updated_at:
            try:
                # Convert to datetime object and format
                dt = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")
            except:
                formatted_date = updated_at
        else:
            formatted_date = 'Not available'
            
        # Populate search tab with the found record
        self.search_tree.insert("", "end", values=(
            record['work_id'],
            record['project_name'],
            record['employee_name'],
            record['location'],
            record['client_name'],
            record['setup_date'],
            record['event_date'],
            formatted_date
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
            messagebox.showwarning("Error", f"Record with Work ID {work_id} not found")
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
        
        # Handle setup_date - use set_date() for DateEntry widget
        if record.get('setup_date'):
            try:
                # Parse the date string into datetime object
                if isinstance(record['setup_date'], str):
                    try:
                        dt = datetime.strptime(record['setup_date'], '%Y-%m-%d')
                    except ValueError:
                        dt = datetime.strptime(record['setup_date'], '%Y-%m-%d')
                    self.setup_date.set_date(dt)
                else:
                    self.setup_date.set_date(record['setup_date'])
            except Exception as e:
                logger.error(f"Error setting setup date: {str(e)}")
                self.setup_date.set_date(datetime.now())
        else:
            self.setup_date.set_date(datetime.now())  # Set to current date if null
        
        self.project_name.delete(0, tk.END)
        self.project_name.insert(0, record['project_name'])
        
        # Handle event_date - use set_date() for DateEntry widget
        if record.get('event_date'):
            try:
                if isinstance(record['event_date'], str):
                    try:
                        dt = datetime.strptime(record['event_date'], '%Y-%m-%d')
                    except ValueError:
                        dt = datetime.strptime(record['event_date'], '%Y-%m-%d')
                    self.event_date.set_date(dt)
                else:
                    self.event_date.set_date(record['event_date'])
            except Exception as e:
                logger.error(f"Error setting event date: {str(e)}")
                self.event_date.set_date(datetime.now())
        else:
            self.event_date.set_date(datetime.now())  # Set to current date if null
        
        # Clear existing table entries and add enough rows
        self.clear_table()
        
        # Add rows for all inventory items
        for _ in range(len(record.get('inventory_items', [])) - len(self.table_entries)):
            self.add_table_row()
        
        # Fill in the inventory items
        for i, item in enumerate(record.get('inventory_items', [])):
            if i >= len(self.table_entries):
                break
                
            row = self.table_entries[i]
            # Ensure we have all the fields we need
            fields = [
                'zone_active', 'sno', 'name', 'description', 
                'quantity', 'comments', 'total', 'unit', 
                'per_unit_power', 'total_power', 'status', 'poc', 'RecQty'
            ]
            
            for col, field in enumerate(fields):
                if col < len(row):  # Make sure we don't exceed row length
                    value = str(item.get(field, ''))
                    if col == 2:  # Inventory column (InventoryComboBox)
                        row[col].set(value)  # Set the inventory name
                    elif col == 10:  # Status column (Combobox)
                        try:
                            row[col].set(value if value in self.status_options else self.status_options[0])
                        except Exception as e:
                            logger.error(f"Error setting status for row {i}: {str(e)}")
                            row[col].set(self.status_options[0])
                    else:  # Regular Entry
                        row[col].delete(0, tk.END)
                        row[col].insert(0, value)
            
        # Switch back to form view
        self.tab_control.select(0)
        
        # Set fields to readonly initially
        self.set_fields_readonly(True)
        self.edit_btn.config(state=tk.NORMAL)
        self.update_btn.config(state=tk.DISABLED)

    def clear_table(self):
        """Clear all table entries except the first row"""
        # Remove all rows except first one
        while len(self.table_entries) > 1:
            self.remove_table_row()
        
        # Clear the first row
        if self.table_entries:
            for entry in self.table_entries[0]:
                entry.delete(0, tk.END)

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
        """Update the record in database via API with multiple rows"""
        try:
            work_id = self.work_id.get()
            if not work_id:
                messagebox.showwarning("Warning", "Work ID is required for update")
                return
                
            # Prepare the complete data package
            data = {
                'work_id': work_id,
                'employee_name': self.employee_name.get() or '',
                'location': self.location.get() or '',
                'client_name': self.client_name.get() or '',
                'setup_date': self.setup_date.get() or '',
                'project_name': self.project_name.get() or '',
                'event_date': self.event_date.get() or '',
                'inventory_items': []
            }
            
            # Process all rows - no limit
            for row_idx, row in enumerate(self.table_entries, start=1):
                # Only process rows with inventory name (skip empty rows)
                if not row[2].get().strip():
                    continue
                    
                try:
                    item = {
                        'zone_active': row[0].get() or 'General',
                        'sno': row[1].get() or str(row_idx),
                        'name': row[2].get(),
                        'description': row[3].get() or '',
                        'quantity': self._validate_number(row[4].get(), default=1),
                        'comments': row[5].get() or '',
                        'total': self._validate_number(row[6].get(), default=0),
                        'unit': row[7].get() or 'pcs',
                        'per_unit_power': self._validate_number(row[8].get(), default=0),
                        'total_power': self._validate_number(row[9].get(), default=0),
                        'status': row[10].get(),  # Simplified - just get the Combobox value
                        'poc': row[11].get() or '',
                        'RecQty': row[12].get() if len(row) > 12 else ''
                    }
                    data['inventory_items'].append(item)
                except Exception as e:
                    logger.error(f"Error processing row {row_idx}: {str(e)}")
                    continue
                        
            if not data['inventory_items']:
                messagebox.showwarning("Warning", "No valid inventory items to update")
                return
                
            logger.debug(f"Prepared update data for {work_id} with {len(data['inventory_items'])} items")
            
            # Save and verify
            if not self.save_to_db(data):
                raise Exception("Failed to persist changes to database")
                
            # Force complete refresh
            self._complete_refresh(work_id)
            
            messagebox.showinfo("Success", f"Updated {len(data['inventory_items'])} items successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {str(e)}")
            logger.error(f"Update error: {str(e)}", exc_info=True)

    def _validate_number(self, value, default=0):
        """Ensure numeric fields are valid"""
        try:
            if not value:
                return default
            return float(value) if '.' in value else int(value)
        except:
            return default

    def _complete_refresh(self, work_id):
        """Complete refresh after update"""
        try:
            # Reload all data
            self.load_submitted_forms()
            
            # Reload this specific project
            self.load_project_data(work_id)
            
            # Reset UI state
            self.set_fields_readonly(True)
            self.edit_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)
            
            # Ensure visibility in UI
            self.tab_control.select(self.submitted_tab)
            self._scroll_to_project(work_id)
            
        except Exception as e:
            logger.error(f"Refresh error: {str(e)}", exc_info=True)

    def _scroll_to_project(self, work_id):
        """Scroll to the updated project in the treeview"""
        for item in self.submitted_tree.get_children():
            if self.submitted_tree.item(item)['values'][0] == work_id:
                self.submitted_tree.selection_set(item)
                self.submitted_tree.see(item)
                break


    def refresh_after_update(self, work_id):
        """Refresh the form after successful update"""
        try:
            # Clear and reload the submitted forms list
            self.load_submitted_forms()
            
            # Reload the current project data
            self.load_project_data(work_id)
            
            # Switch to readonly mode
            self.set_fields_readonly(True)
            self.edit_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)
            
            # Ensure the updated project is visible in the list
            self.tab_control.select(self.submitted_tab)
            
            # Scroll to the updated project in the treeview
            for item in self.submitted_tree.get_children():
                if self.submitted_tree.item(item)['values'][0] == work_id:
                    self.submitted_tree.selection_set(item)
                    self.submitted_tree.see(item)
                    break
                    
        except Exception as e:
            logger.error(f"Refresh after update failed: {str(e)}", exc_info=True)

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
            if col == 2:  # Inventory column - use InventoryComboBox
                combo_frame = tk.Frame(self.scrollable_frame)
                combo_frame.grid(row=current_rows+1, column=col, sticky="ew", padx=2, pady=2)
                
                combo = InventoryComboBox(combo_frame)
                combo.pack(fill=tk.X, expand=True)
                
                # Bind selection to update related fields
                combo.bind('<<ComboboxSelected>>', 
                        lambda e, r=row_entries: self._update_inventory_fields(r, e))
                row_entries.append(combo)
            elif col == 10:  # Status column
                status_var = tk.StringVar()
                combo = ttk.Combobox(
                    self.scrollable_frame,
                    textvariable=status_var,
                    values=self.status_options,
                    state="state",
                    font=('Helvetica', 9)
                )
                combo.set(self.status_options[0])  # Set default status
                combo.grid(row=current_rows+1, column=col, sticky="ew", padx=2, pady=2)
                row_entries.append(combo)
            else:
                entry = tk.Entry(self.scrollable_frame, 
                            font=('Helvetica', 9), 
                            width=self.original_column_widths[col])
                if col == 12:  # RecQty column (index 12) - make it readonly
                    entry.config(state='readonly')
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
        """Handle form submission with multiple inventory items"""
        try:
            # Get the current work_id
            work_id = self.work_id.get()
            if not work_id:
                messagebox.showwarning("Warning", "Work ID is required")
                return

            # Basic validation
            if not (self.employee_name.get() or self.client_name.get() or self.project_name.get()):
                messagebox.showwarning("Warning", "Please fill in at least one required field")
                return

            # Prepare data with all fields
            data = {
                'work_id': work_id,
                'employee_name': self.employee_name.get(),
                'location': self.location.get(),
                'client_name': self.client_name.get(),
                'setup_date': self.setup_date.get(),
                'project_name': self.project_name.get(),
                'event_date': self.event_date.get(),
                'submitted_by': "inventory-admin",  # Add this required field
                'inventory_items': []
            }

            # Add all inventory items with proper field mapping
            for row in self.table_entries:
                # Only add rows with at least name and quantity
                if row[2].get() and row[4].get():  # name and quantity fields
                    item = {
                        'work_id': work_id,
                        'zone_active': row[0].get() or "Default Zone",  # Provide default if empty
                        'sno': row[1].get() or "",  # Optional field
                        'name': row[2].get(),
                        'description': row[3].get() or "",  # Optional field
                        'quantity': int(row[4].get()) if row[4].get().isdigit() else 1,  # Convert to int
                        'comments': row[5].get() or "",  # Optional field
                        'total': row[6].get() if row[6].get().isdigit() else 0,  # Handle optional total field
                        'unit': row[7].get() or "pcs",  # Provide default if empty
                        'per_unit_power': float(row[8].get()) if row[8].get() and row[8].get().replace('.','',1).isdigit() else 0.0,
                        'total_power': float(row[9].get()) if row[9].get() and row[9].get().replace('.','',1).isdigit() else 0.0,
                        'status': row[10].get(),
                        'poc': row[11].get() or "",  # Optional field
                        'RecQty': row[12].get() if len(row) > 12 else ""  # Handle optional RecQty field
                    }
                    data['inventory_items'].append(item)

            if not data['inventory_items']:
                messagebox.showwarning("Warning", "At least one inventory item with name and quantity is required")
                return

            logger.debug(f"Sending payload: {data}")

            # Try to save to API
            if not self.save_to_db(data):
                raise Exception("Failed to save to database")

            messagebox.showinfo("Success", "Form submitted successfully")
            logger.info(f"Form submitted: {data}")

            # Clear form and generate new WorkID
            self.clear_form()
            self.generate_work_id()

            # Refresh submitted forms tab
            self.load_submitted_forms()
            self.tab_control.select(self.submitted_tab)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit form: {str(e)}")
            logger.error(f"Submit failed: {str(e)}")

    def clear_form(self):
        """Clear all form fields and generate new Work ID"""
        try:
            self.project_id.delete(0, tk.END)
            self.employee_name.delete(0, tk.END)
            self.location.delete(0, tk.END)
            self.client_name.delete(0, tk.END)
            
            # Clear DateEntry widgets properly
            self.setup_date.set_date(datetime.now().strftime('%Y-%m-%d'))
            self.project_name.delete(0, tk.END)
            self.event_date.set_date(datetime.now().strftime('%Y-%m-%d'))
            
            # Clear table entries
            for row in self.table_entries:
                for entry in row:
                    entry.delete(0, tk.END)
            
            # Generate new Work ID
            self.generate_work_id()
            
            # Set fields to editable state
            self.set_fields_readonly(False)
            
            messagebox.showinfo("Cleared", "Form has been cleared")
            logger.info("Form cleared successfully")
        except Exception as e:
            messagebox.showerror("Clear Error", f"Failed to clear form: {str(e)}")
            logger.error(f"Clear failed: {str(e)}")

    def refresh_data(self):
        """Refresh the form and data lists"""
        try:
            # Clear existing items
            self.clear_form()
            # If we have a work_id loaded, refresh that specific record
            current_work_id = self.work_id.get()              
            messagebox.showinfo("Refreshed", "Data has been refreshed")
            logger.info("Data refreshed successfully")
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh data: {str(e)}")
            logger.error(f"Refresh failed: {str(e)}")

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing To Event window")
        self.window.destroy()
        self.parent.deiconify()