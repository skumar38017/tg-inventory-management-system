import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import platform
import logging

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
        self.set_fields_readonly(False)  # Start with fields editable for new entries
        
        logger.info("To Event window opened successfully")

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
        self.project_id.config(state='normal')  # Project ID should always be editable
        
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
        # Header section - Clock in row 0
        clock_frame = tk.Frame(self.window)
        clock_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=0)
        clock_frame.grid_columnconfigure(0, weight=1)  # Left spacer
        clock_frame.grid_columnconfigure(1, weight=0)  # Center for clock
        clock_frame.grid_columnconfigure(2, weight=1)  # Right spacer

        # Clock in absolute center at top
        self.clock_label = tk.Label(clock_frame, font=('Helvetica', 8))
        self.clock_label.grid(row=0, column=1, sticky='n', pady=(0,0))
        self.update_clock()

        # Company info in row 1 (top-right corner)
        company_frame = tk.Frame(self.window)
        company_frame.grid(row=1, column=0, columnspan=2, sticky="e", padx=10, pady=0)
        company_frame.grid_columnconfigure(0, weight=1)  # Left spacer

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

        # Title section in row 2
        title_frame = tk.Frame(self.window)
        title_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Centered company name
        tk.Label(title_frame, 
               text="Tagglabs Experiential Pvt. Ltd",
               font=('Helvetica', 14, 'bold')).pack()
        
        # Centered inventory list title
        tk.Label(title_frame, 
               text="INVENTORY LIST",
               font=('Helvetica', 12, 'bold')).pack()

        # Information fields in row 3
        info_frame = tk.Frame(self.window)
        info_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # First row - Project ID and buttons
        tk.Label(info_frame, text="Project ID:", font=('Helvetica', 9)).grid(row=0, column=0, sticky='e', padx=2)
        self.project_id = tk.Entry(info_frame, font=('Helvetica', 9), width=15)
        self.project_id.grid(row=0, column=1, sticky='w', padx=2)
        
        # Fetch Details button
        self.fetch_btn = tk.Button(info_frame, text="Fetch Details", command=self.fetch_record,
                                 font=('Helvetica', 9, 'bold'))
        self.fetch_btn.grid(row=0, column=2, padx=5)
        
        # Edit and Update buttons
        self.edit_btn = tk.Button(info_frame, text="Edit", command=self.edit_record,
                                font=('Helvetica', 9, 'bold'), state=tk.NORMAL)
        self.edit_btn.grid(row=0, column=3, padx=5)
        
        self.update_btn = tk.Button(info_frame, text="Update", command=self.update_record,
                                  font=('Helvetica', 9, 'bold'), state=tk.DISABLED)
        self.update_btn.grid(row=0, column=4, padx=5)

        # Second row - all fields in one line {Title Info}
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
                
        # Separator line
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # Inventory table in row 5
        self.table_frame = tk.Frame(self.window)
        self.table_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Create a canvas and scrollbars for the table
        self.canvas = tk.Canvas(self.table_frame)
        
        # Vertical scrollbar - fixed to scroll top-to-bottom
        self.v_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.pack(side="right", fill="y")

        # Horizontal scrollbar
        self.h_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.pack(side="bottom", fill="x")

        # Create the scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # Create window in canvas - this is the key change for scroll direction
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Make sure the canvas starts at the top
        self.canvas.yview_moveto(0)

        # Table headers
        self.headers = [
            "Zone/Activity", "Sr. No.", "Inventory", "Description/Specifications",
            "Quantity", "Comments", "Total", "Units", 
            "Per Unit Power Consumption (Watt/H)", "Total Power Consumption (Watt)",
            "Status (purchased/not purchased)", "POC"
        ]

        # Store original column widths
        self.original_column_widths = [20 if col not in [4,6,7,8,9] else 15 for col in range(len(self.headers))]
        
        for col, header in enumerate(self.headers):
            tk.Label(self.scrollable_frame, text=header, font=('Helvetica', 9, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")

        # Create entry fields for each column
        self.table_entries = []
        for row in range(1, 6):  # Create 5 empty rows
            row_entries = []
            for col in range(len(self.headers)):
                entry = tk.Entry(self.scrollable_frame, font=('Helvetica', 9), 
                               width=self.original_column_widths[col])
                entry.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                row_entries.append(entry)
            self.table_entries.append(row_entries)

        # Bottom buttons in row 6
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Wrap button to adjust columns (toggle)
        self.wrap_btn = tk.Button(button_frame, text="Wrap", command=self.toggle_wrap,
                                font=('Helvetica', 10, 'bold'))
        self.wrap_btn.pack(side=tk.LEFT, padx=5)

        # Remove row button
        remove_row_btn = tk.Button(button_frame, text="Remove Row", command=self.remove_table_row,
                                 font=('Helvetica', 10, 'bold'))
        remove_row_btn.pack(side=tk.LEFT, padx=5)

        # Add row button
        add_row_btn = tk.Button(button_frame, text="Add Row", command=self.add_table_row,
                              font=('Helvetica', 10, 'bold'))
        add_row_btn.pack(side=tk.LEFT, padx=5)

        # Submit button
        submit_btn = tk.Button(button_frame, text="Submit", command=self.submit_form,
                             font=('Helvetica', 10, 'bold'))
        submit_btn.pack(side=tk.LEFT, padx=5)

        # Return button on right
        return_button = tk.Button(button_frame, 
                                text="Return to Main", 
                                command=self.on_close,
                                font=('Helvetica', 10, 'bold'),
                                width=15)
        return_button.pack(side=tk.RIGHT, padx=5)

        # Grid configuration
        self.window.grid_rowconfigure(0, weight=0)  # Clock
        self.window.grid_rowconfigure(1, weight=0)  # Company info
        self.window.grid_rowconfigure(2, weight=0)  # Title
        self.window.grid_rowconfigure(3, weight=0)  # Info fields
        self.window.grid_rowconfigure(4, weight=0)  # Separator
        self.window.grid_rowconfigure(5, weight=1)  # Table
        self.window.grid_rowconfigure(6, weight=0)  # Buttons
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

    def fetch_record(self):
        """Fetch record based on Project ID"""
        project_id = self.project_id.get()
        if not project_id:
            messagebox.showwarning("Warning", "Please enter a Project ID")
            return
            
        try:
            # Here you would fetch the record from your database
            # For demonstration, we'll use mock data
            mock_data = self.get_mock_data(project_id)
            
            if not mock_data:
                messagebox.showwarning("Warning", f"No record found for Project ID: {project_id}")
                return
                
            # Populate the fields
            self.employee_name.delete(0, tk.END)
            self.employee_name.insert(0, mock_data['employee_name'])
            
            self.location.delete(0, tk.END)
            self.location.insert(0, mock_data['location'])
            
            self.client_name.delete(0, tk.END)
            self.client_name.insert(0, mock_data['client_name'])
            
            self.setup_date.delete(0, tk.END)
            self.setup_date.insert(0, mock_data['setup_date'])
            
            self.project_name.delete(0, tk.END)
            self.project_name.insert(0, mock_data['project_name'])
            
            self.event_date.delete(0, tk.END)
            self.event_date.insert(0, mock_data['event_date'])
            
            # Clear existing table data
            for row in self.table_entries:
                for entry in row:
                    entry.delete(0, tk.END)
            
            # Populate table with inventory items
            for i, item in enumerate(mock_data['inventory_items']):
                if i >= len(self.table_entries):
                    self.add_table_row()
                
                self.table_entries[i][0].insert(0, item['zone_activity'])
                self.table_entries[i][1].insert(0, item['sr_no'])
                self.table_entries[i][2].insert(0, item['inventory'])
                self.table_entries[i][3].insert(0, item['description'])
                self.table_entries[i][4].insert(0, item['quantity'])
                self.table_entries[i][5].insert(0, item['comments'])
                self.table_entries[i][6].insert(0, item['total'])
                self.table_entries[i][7].insert(0, item['units'])
                self.table_entries[i][8].insert(0, item['power_per_unit'])
                self.table_entries[i][9].insert(0, item['total_power'])
                self.table_entries[i][10].insert(0, item['status'])
                self.table_entries[i][11].insert(0, item['poc'])
            
            # Set fields to readonly initially
            self.set_fields_readonly(True)
            self.edit_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)
            
            messagebox.showinfo("Success", "Record loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch record: {str(e)}")
            logger.error(f"Fetch failed: {str(e)}")

    def get_mock_data(self, project_id):
        """Generate mock data for demonstration"""
        # In a real application, you would query your database here
        if project_id == "PRJ-001":
            return {
                'employee_name': "John Doe",
                'location': "Gurugram",
                'client_name': "ABC Corp",
                'setup_date': "2023-11-15",
                'project_name': "Product Launch",
                'event_date': "2023-11-20",
                'project_id': "PRJ-001",
                'inventory_items': [
                    {
                        'zone_activity': "Main Stage",
                        'sr_no': "1",
                        'inventory': "LED Screen",
                        'description': "5x3m 4K Resolution",
                        'quantity': "2",
                        'comments': "",
                        'total': "2",
                        'units': "pcs",
                        'power_per_unit': "500",
                        'total_power': "1000",
                        'status': "purchased",
                        'poc': "Vendor A"
                    },
                    {
                        'zone_activity': "Lounge Area",
                        'sr_no': "2",
                        'inventory': "Sofa Set",
                        'description': "3-seater, black leather",
                        'quantity': "4",
                        'comments': "",
                        'total': "4",
                        'units': "pcs",
                        'power_per_unit': "0",
                        'total_power': "0",
                        'status': "purchased",
                        'poc': "Vendor B"
                    }
                ]
            }
        return None

    def edit_record(self):
        """Enable editing of the record"""
        self.set_fields_readonly(False)
        self.edit_btn.config(state=tk.DISABLED)
        self.update_btn.config(state=tk.NORMAL)
        logger.info("Editing record")

    def update_record(self):
        """Update the record"""
        try:
            # Validate required fields
            if not self.employee_name.get() or not self.client_name.get():
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
                
            project_id = self.project_id.get()
            if not project_id:
                messagebox.showwarning("Warning", "Project ID is required for update")
                return
                
            # Here you would save the updated data to your database
            # For demonstration, we'll just show a message
            
            # Prepare the data to be saved
            data = {
                'employee_name': self.employee_name.get(),
                'location': self.location.get(),
                'client_name': self.client_name.get(),
                'setup_date': self.setup_date.get(),
                'project_name': self.project_name.get(),
                'event_date': self.event_date.get(),
                'project_id': project_id,
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
            
            # In a real app, you would call your database update function here
            # db_update_record(project_id, data)
            
            messagebox.showinfo("Success", "Record updated successfully")
            logger.info(f"Record updated: {data}")
            
            # Set fields back to readonly
            self.set_fields_readonly(True)
            self.edit_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)
            
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
        # Calculate max width for each column
        col_widths = [len(header) for header in self.headers]
        
        # Check all entries in each column
        for row in self.table_entries:
            for col, entry in enumerate(row):
                content = entry.get()
                if content:
                    col_widths[col] = max(col_widths[col], len(content))
        
        # Apply the new widths
        for col, width in enumerate(col_widths):
            # Add some padding and limit max width
            adjusted_width = min(width + 5, 50)  # Max width of 50 characters
            self.scrollable_frame.grid_columnconfigure(col, minsize=adjusted_width * 8)  # Approximate pixel width
            
        # Update the canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.xview_moveto(0)  # Reset horizontal scroll to left

    def reset_columns(self):
        """Reset columns to their original widths"""
        for col, width in enumerate(self.original_column_widths):
            self.scrollable_frame.grid_columnconfigure(col, minsize=width * 10)  # Reset to original width
            
        # Update the canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.xview_moveto(0)  # Reset horizontal scroll to left

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
        
        # Update the canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def remove_table_row(self):
        """Remove the last row from the table"""
        if len(self.table_entries) <= 1:  # Keep at least one row
            messagebox.showwarning("Warning", "Cannot remove the last row")
            return
            
        last_row = self.table_entries.pop()
        for entry in last_row:
            entry.destroy()
        
        # Update the canvas scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def submit_form(self):
        """Handle form submission"""
        # Validate required fields
        if not self.employee_name.get() or not self.client_name.get():
            messagebox.showwarning("Warning", "Please fill in all required fields")
            return
            
        # Process the data
        data = {
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
        
        # In a real app, you would call your database insert function here
        # db_insert_record(data)
        
        messagebox.showinfo("Success", "Form submitted successfully")
        logger.info(f"Form submitted: {data}")

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing To Event window")
        self.window.destroy()
        self.parent.deiconify()  # Show parent window