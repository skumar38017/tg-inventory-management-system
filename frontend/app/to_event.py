import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import platform
import logging
import random
import string

logger = logging.getLogger(__name__)

class ToEventWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs - To Event")

        # Track wrap state
        self.is_wrapped = False
        self.original_column_widths = []
        
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
        
        logger.info("To Event window opened successfully")

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
        
        # First row - IDs and buttons (now only Project ID)
        tk.Label(info_frame, text="Project ID:", font=('Helvetica', 9)).grid(row=0, column=0, sticky='e', padx=2)
        self.project_id = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.project_id.grid(row=0, column=1, sticky='w', padx=2)
                
        self.fetch_btn = tk.Button(info_frame, text="Fetch Details", command=self.fetch_record,
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
        
        # Moved Work ID to here (right-aligned at the end)
        tk.Label(info_frame, text="Work ID:", font=('Helvetica', 9)).grid(row=1, column=12, sticky='e', padx=2)
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

        # Recent Projects frame
        recent_frame = tk.Frame(self.window, bg="white", bd=1, relief=tk.SOLID)
        recent_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=(5,0))
        
        tk.Label(recent_frame, text="Recent Projects Details", font=('Helvetica', 10, 'bold'), 
               bg="white").pack(anchor="w", padx=5, pady=2)

        self.recent_tree = ttk.Treeview(recent_frame, height=5, 
                                      columns=("WorkID", "Employee", "Location", "Client", "Setup", "Project", "Event"),
                                      show="headings")
        
        self.recent_tree.heading("WorkID", text="Project ID")
        self.recent_tree.heading("Employee", text="Employee Name")
        self.recent_tree.heading("Location", text="Location")
        self.recent_tree.heading("Client", text="Client Name")
        self.recent_tree.heading("Setup", text="Setup Date")
        self.recent_tree.heading("Project", text="Project Name")
        self.recent_tree.heading("Event", text="Event Date")
        
        self.recent_tree.column("WorkID", width=80)
        self.recent_tree.column("Employee", width=120)
        self.recent_tree.column("Location", width=100)
        self.recent_tree.column("Client", width=120)
        self.recent_tree.column("Setup", width=100)
        self.recent_tree.column("Project", width=150)
        self.recent_tree.column("Event", width=100)
        
        tree_scroll = ttk.Scrollbar(recent_frame, orient="vertical", command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.recent_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

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
        self.window.grid_rowconfigure(6, weight=0)
        self.window.grid_rowconfigure(7, weight=0)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

    def fetch_record(self):
        """Fetch record based on Project ID and match with WorkID"""
        project_id = self.project_id.get()
        if not project_id:
            messagebox.showwarning("Warning", "Please enter a Project ID")
            return
            
        try:
            # TODO: Replace with actual database call
            # records = database.get_records_by_project_id(project_id)
            
            # Sample data for demonstration
            records = [
                {
                    'work_id': 'PRJ12345',
                    'employee_name': 'John Doe',
                    'location': 'Gurugram',
                    'client_name': 'ABC Corp',
                    'setup_date': '2023-01-15',
                    'project_name': 'Product Launch',
                    'event_date': '2023-01-20',
                    'project_id': 'PROJ001'
                },
                {
                    'work_id': 'PRJ67890',
                    'employee_name': 'Jane Smith',
                    'location': 'Delhi',
                    'client_name': 'XYZ Inc',
                    'setup_date': '2023-02-10',
                    'project_name': 'Conference',
                    'event_date': '2023-02-15',
                    'project_id': 'PROJ001'
                }
            ]
            
            if not records:
                messagebox.showwarning("Warning", f"No records found for Project ID: {project_id}")
                return
                
            # Clear the recent projects tree
            for item in self.recent_tree.get_children():
                self.recent_tree.delete(item)
                
            # Populate the tree with matching records
            for record in records:
                self.recent_tree.insert("", "end", values=(
                    record.get('work_id', ''),
                    record.get('employee_name', ''),
                    record.get('location', ''),
                    record.get('client_name', ''),
                    record.get('setup_date', ''),
                    record.get('project_name', ''),
                    record.get('event_date', '')
                ))
            
            # Bind double-click event to load project details
            self.recent_tree.bind("<Double-1>", self.load_project_from_list)
            
            messagebox.showinfo("Success", f"Found {len(records)} matching records")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch records: {str(e)}")
            logger.error(f"Fetch failed: {str(e)}")

    def load_project_from_list(self, event):
        """Load selected project details when double-clicked"""
        selected_item = self.recent_tree.selection()
        if selected_item:
            item = self.recent_tree.item(selected_item)
            project_data = item['values']
            
            # Populate the fields from selected record
            self.work_id.config(state='normal')
            self.work_id.delete(0, tk.END)
            self.work_id.insert(0, project_data[0])
            self.work_id.config(state='readonly')
            
            self.employee_name.delete(0, tk.END)
            self.employee_name.insert(0, project_data[1])
            
            self.location.delete(0, tk.END)
            self.location.insert(0, project_data[2])
            
            self.client_name.delete(0, tk.END)
            self.client_name.insert(0, project_data[3])
            
            self.setup_date.delete(0, tk.END)
            self.setup_date.insert(0, project_data[4])
            
            self.project_name.delete(0, tk.END)
            self.project_name.insert(0, project_data[5])
            
            self.event_date.delete(0, tk.END)
            self.event_date.insert(0, project_data[6])
            
            # Set fields to readonly initially
            self.set_fields_readonly(True)
            self.edit_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)

    def edit_record(self):
        """Enable editing of the record"""
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
                'work_id': work_id,
                'employee_name': self.employee_name.get(),
                'location': self.location.get(),
                'client_name': self.client_name.get(),
                'setup_date': self.setup_date.get(),
                'project_name': self.project_name.get(),
                'event_date': self.event_date.get(),
                'project_id': self.project_id.get(),
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
            
            # TODO: Replace with actual database call
            # database.update_record(data)
            
            messagebox.showinfo("Success", "Record updated successfully")
            logger.info(f"Record updated: {data}")
            
            # Set fields back to readonly
            self.set_fields_readonly(True)
            self.edit_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)
            
            # Refresh recent projects list
            self.fetch_record()
            
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
            'work_id': self.work_id.get(),
            'employee_name': self.employee_name.get(),
            'location': self.location.get(),
            'client_name': self.client_name.get(),
            'setup_date': self.setup_date.get(),
            'project_name': self.project_name.get(),
            'event_date': self.event_date.get(),
            'project_id': self.project_id.get(),
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
        
        # TODO: Replace with actual database call
        # database.insert_record(data)
        
        messagebox.showinfo("Success", "Form submitted successfully")
        logger.info(f"Form submitted: {data}")
        
        # Clear form and generate new WorkID
        self.clear_form()
        self.generate_work_id()

    def clear_form(self):
        """Clear all form fields"""
        self.employee_name.delete(0, tk.END)
        self.location.delete(0, tk.END)
        self.client_name.delete(0, tk.END)
        self.setup_date.delete(0, tk.END)
        self.project_name.delete(0, tk.END)
        self.event_date.delete(0, tk.END)
        self.project_id.delete(0, tk.END)
        
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