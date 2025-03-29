# frontend/app/damage_inventory.py

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import platform
import logging

logger = logging.getLogger(__name__)

class DamageWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Inventory Damage/Waste/Not Working/Lost")

        # Track wrap state
        self.is_wrapped = False
        self.original_column_widths = []
        self.submitted_data = []  # Store all submitted entries
        
        # Variables for edit functionality
        self.selected_items = []
        self.edit_mode = False
        self.current_edit_id = None
        self.checkbox_vars = []
        
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
        
        logger.info("Damage/Waste/Not Working/Lost window opened successfully")

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
               text="DAMAGE/WASTE/NOT WORKING/LOST INVENTORY",
               font=('Helvetica', 12, 'bold')).pack()

        # Search frame in row 3
        search_frame = tk.Frame(self.window)
        search_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Search fields
        tk.Label(search_frame, text="Inventory ID:", font=('Helvetica', 9)).grid(row=0, column=0, sticky='e', padx=5)
        self.search_inventory_id = tk.Entry(search_frame, font=('Helvetica', 9), width=20)
        self.search_inventory_id.grid(row=0, column=1, sticky='w', padx=5)
        
        tk.Label(search_frame, text="Project ID:", font=('Helvetica', 9)).grid(row=0, column=2, sticky='e', padx=5)
        self.search_project_id = tk.Entry(search_frame, font=('Helvetica', 9), width=20)
        self.search_project_id.grid(row=0, column=3, sticky='w', padx=5)
        
        tk.Label(search_frame, text="Product ID:", font=('Helvetica', 9)).grid(row=0, column=4, sticky='e', padx=5)
        self.search_product_id = tk.Entry(search_frame, font=('Helvetica', 9), width=20)
        self.search_product_id.grid(row=0, column=5, sticky='w', padx=5)

        # Search button
        search_btn = tk.Button(search_frame, text="Search", command=self.search_inventory, 
                             font=('Helvetica', 9, 'bold'))
        search_btn.grid(row=0, column=6, sticky='e', padx=5)

        # Separator line
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # Main content frame (will contain both input and display areas)
        content_frame = tk.Frame(self.window)
        content_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        # Configure grid weights for content frame
        content_frame.grid_rowconfigure(0, weight=1)  # Input frame
        content_frame.grid_rowconfigure(1, weight=0)  # Separator
        content_frame.grid_rowconfigure(2, weight=1)  # Display frames
        content_frame.grid_columnconfigure(0, weight=1)

        # Input frame (top half)
        input_frame = tk.Frame(content_frame)
        input_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        
        # Inventory table frame in input frame
        self.table_frame = tk.Frame(input_frame)
        self.table_frame.pack(fill="both", expand=True)
        
        # Create a canvas and horizontal scrollbar for the input table
        self.input_canvas = tk.Canvas(self.table_frame)
        self.input_h_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.input_canvas.xview)
        self.input_h_scrollbar.pack(side="bottom", fill="x")

        # Create the scrollable frame for input
        self.scrollable_input_frame = tk.Frame(self.input_canvas)
        self.scrollable_input_frame.bind(
            "<Configure>",
            lambda e: self.input_canvas.configure(
                scrollregion=self.input_canvas.bbox("all")
            )
        )

        # Create window in canvas
        self.input_canvas.create_window((0, 0), window=self.scrollable_input_frame, anchor="nw")
        self.input_canvas.configure(xscrollcommand=self.input_h_scrollbar.set)
        self.input_canvas.pack(side="left", fill="both", expand=True)

        # Table headers with all fields
        self.headers = [
            "Zone/Activity", "Sr. No.", "InventoryID", "ProductID", "ProjectID", 
            "Inventory", "Description/Specifications", "Qty", "Comments", 
            "Status", "Received Date", "Received By", "Check Status",
            "Employee Name", "Location", "Project Name", "Event Date"
        ]
        
        # Define original column widths (in characters)
        self.original_column_widths = {
            0: 15,   # Zone/Activity
            1: 8,    # Sr. No.
            2: 12,   # InventoryID
            3: 12,  # ProductID
            4: 12,  # ProjectID
            5: 20,  # Inventory
            6: 25,  # Description/Specifications
            7: 5,   # Qty
            8: 20,  # Comments
            9: 12,  # Status
            10: 12, # Received Date
            11: 15, # Received By
            12: 15, # Check Status
            13: 15, # Employee Name
            14: 12, # Location
            15: 15, # Project Name
            16: 12  # Event Date
        }
        
        # Create headers (row 0)
        for col, header in enumerate(self.headers):
            tk.Label(self.scrollable_input_frame, text=header, font=('Helvetica', 15, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")
            # Set initial column widths
            self.scrollable_input_frame.columnconfigure(col, minsize=self.original_column_widths[col] * 8)

        # Create single row of entry fields (row 1)
        self.table_entries = []
        row_entries = []
        for col in range(len(self.headers)):
            entry = tk.Entry(self.scrollable_input_frame, font=('Helvetica', 15), 
                           width=self.original_column_widths[col])
            entry.grid(row=1, column=col, sticky="ew", padx=2, pady=2)
            row_entries.append(entry)
        self.table_entries.append(row_entries)

        # Separator between input and display areas
        separator = ttk.Separator(content_frame, orient='horizontal')
        separator.grid(row=1, column=0, sticky="ew", pady=2)

        # Display frames (bottom half)
        display_frame = tk.Frame(content_frame)
        display_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        
        # Create notebook for display tabs
        self.display_notebook = ttk.Notebook(display_frame)
        self.display_notebook.pack(fill="both", expand=True)
        
        # Search Results tab
        self.search_results_frame = tk.Frame(self.display_notebook)
        self.display_notebook.add(self.search_results_frame, text="Search Results")

        # Edit/Update tab
        self.edit_frame = tk.Frame(self.display_notebook)
        self.display_notebook.add(self.edit_frame, text="Edit/Update")
        
        # Submission History tab
        self.submission_history_frame = tk.Frame(self.display_notebook)
        self.display_notebook.add(self.submission_history_frame, text="Submission History")
        
        # Configure all display frames
        self.setup_search_results_frame()
        self.setup_edit_frame()
        self.setup_submission_history_frame()

        # Bottom buttons in row 6
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Wrap button to adjust columns (toggle)
        self.wrap_btn = tk.Button(button_frame, text="Wrap", command=self.toggle_wrap,
                                font=('Helvetica', 10, 'bold'))
        self.wrap_btn.pack(side=tk.LEFT, padx=5)

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
        self.window.grid_rowconfigure(3, weight=0)  # Search fields
        self.window.grid_rowconfigure(4, weight=0)  # Separator
        self.window.grid_rowconfigure(5, weight=1)  # Content
        self.window.grid_rowconfigure(6, weight=0)  # Buttons
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

    def setup_search_results_frame(self):
        """Setup the search results display frame"""
        # Create canvas and scrollbars
        self.search_canvas = tk.Canvas(self.search_results_frame)
        self.search_v_scrollbar = ttk.Scrollbar(self.search_results_frame, orient="vertical", command=self.search_canvas.yview)
        self.search_h_scrollbar = ttk.Scrollbar(self.search_results_frame, orient="horizontal", command=self.search_canvas.xview)
        
        # Pack scrollbars
        self.search_v_scrollbar.pack(side="right", fill="y")
        self.search_h_scrollbar.pack(side="bottom", fill="x")
        self.search_canvas.pack(side="left", fill="both", expand=True)
        
        # Create frame inside canvas
        self.search_results_inner_frame = tk.Frame(self.search_canvas)
        self.search_canvas.create_window((0, 0), window=self.search_results_inner_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.search_results_inner_frame.bind(
            "<Configure>",
            lambda e: self.search_canvas.configure(
                scrollregion=self.search_canvas.bbox("all")
            )
        )
        self.search_canvas.configure(yscrollcommand=self.search_v_scrollbar.set)
        self.search_canvas.configure(xscrollcommand=self.search_h_scrollbar.set)

    def setup_edit_frame(self):
        """Setup the edit/update display frame"""
        # Main container frame
        edit_container = tk.Frame(self.edit_frame)
        edit_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Top section - selection and search results
        top_frame = tk.Frame(edit_container)
        top_frame.pack(fill="both", expand=True)
        
        # Create canvas and scrollbars for the edit table
        self.edit_canvas = tk.Canvas(top_frame)
        self.edit_v_scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=self.edit_canvas.yview)
        self.edit_h_scrollbar = ttk.Scrollbar(top_frame, orient="horizontal", command=self.edit_canvas.xview)
        
        # Pack scrollbars
        self.edit_v_scrollbar.pack(side="right", fill="y")
        self.edit_h_scrollbar.pack(side="bottom", fill="x")
        self.edit_canvas.pack(side="left", fill="both", expand=True)
        
        # Create frame inside canvas
        self.edit_inner_frame = tk.Frame(self.edit_canvas)
        self.edit_canvas.create_window((0, 0), window=self.edit_inner_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.edit_inner_frame.bind(
            "<Configure>",
            lambda e: self.edit_canvas.configure(
                scrollregion=self.edit_canvas.bbox("all")
            )
        )
        self.edit_canvas.configure(yscrollcommand=self.edit_v_scrollbar.set)
        self.edit_canvas.configure(xscrollcommand=self.edit_h_scrollbar.set)
        
        # Bottom section - action buttons
        button_frame = tk.Frame(edit_container)
        button_frame.pack(fill="x", pady=5)
        
        # Action buttons
        self.edit_btn = tk.Button(button_frame, text="Edit", command=self.edit_selected,
                                font=('Helvetica', 10, 'bold'), state=tk.DISABLED)
        self.edit_btn.pack(side=tk.LEFT, padx=10)
        
        self.update_btn = tk.Button(button_frame, text="Update", command=self.update_selected,
                                  font=('Helvetica', 10, 'bold'), state=tk.DISABLED)
        self.update_btn.pack(side=tk.LEFT, padx=10)
        
        self.delete_btn = tk.Button(button_frame, text="Delete", command=self.delete_selected,
                                  font=('Helvetica', 10, 'bold'), state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=10)

    def setup_submission_history_frame(self):
        """Setup the submission history display frame"""
        # Create canvas and scrollbars
        self.history_canvas = tk.Canvas(self.submission_history_frame)
        self.history_v_scrollbar = ttk.Scrollbar(self.submission_history_frame, orient="vertical", command=self.history_canvas.yview)
        self.history_h_scrollbar = ttk.Scrollbar(self.submission_history_frame, orient="horizontal", command=self.history_canvas.xview)
        
        # Pack scrollbars
        self.history_v_scrollbar.pack(side="right", fill="y")
        self.history_h_scrollbar.pack(side="bottom", fill="x")
        self.history_canvas.pack(side="left", fill="both", expand=True)
        
        # Create frame inside canvas
        self.history_inner_frame = tk.Frame(self.history_canvas)
        self.history_canvas.create_window((0, 0), window=self.history_inner_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.history_inner_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")
            )
        )
        self.history_canvas.configure(yscrollcommand=self.history_v_scrollbar.set)
        self.history_canvas.configure(xscrollcommand=self.history_h_scrollbar.set)

    def display_search_results(self, results):
        """Display search results in the search results frame"""
        # Clear previous results
        for widget in self.search_results_inner_frame.winfo_children():
            widget.destroy()
        
        # Create headers
        for col, header in enumerate(self.headers):
            tk.Label(self.search_results_inner_frame, text=header, font=('Helvetica', 15, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")
            self.search_results_inner_frame.columnconfigure(col, minsize=self.original_column_widths[col] * 8)
        
        # Display results
        for row_idx, item in enumerate(results, start=1):
            for col, (key, value) in enumerate(item.items()):
                tk.Label(self.search_results_inner_frame, text=value, font=('Helvetica', 15),
                       borderwidth=1, relief="solid", padx=5, pady=2).grid(row=row_idx, column=col, sticky="ew")

    def display_edit_results(self, results):
        """Display search results in the edit frame with checkboxes"""
        # Clear previous results
        for widget in self.edit_inner_frame.winfo_children():
            widget.destroy()
        
        # Create headers with checkbox in first column
        tk.Label(self.edit_inner_frame, text="Select", font=('Helvetica', 15, 'bold'),
                borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=0, sticky="ew")
        
        for col, header in enumerate(self.headers, start=1):
            tk.Label(self.edit_inner_frame, text=header, font=('Helvetica', 15, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")
            self.edit_inner_frame.columnconfigure(col, minsize=self.original_column_widths[col-1] * 8)
        
        # Display results with checkboxes
        self.checkbox_vars = []
        for row_idx, item in enumerate(results, start=1):
            var = tk.BooleanVar()
            self.checkbox_vars.append(var)
            cb = tk.Checkbutton(self.edit_inner_frame, variable=var, 
                              command=lambda: self.toggle_edit_buttons())
            cb.grid(row=row_idx, column=0, sticky="ew", padx=5, pady=2)
            
            for col, (key, value) in enumerate(item.items(), start=1):
                tk.Label(self.edit_inner_frame, text=value, font=('Helvetica', 15),
                       borderwidth=1, relief="solid", padx=5, pady=2).grid(row=row_idx, column=col, sticky="ew")

    def display_submission_history(self):
        """Display all submitted entries in the history frame"""
        # Clear previous history
        for widget in self.history_inner_frame.winfo_children():
            widget.destroy()
        
        # Create headers
        for col, header in enumerate(self.headers):
            tk.Label(self.history_inner_frame, text=header, font=('Helvetica', 15, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")
            self.history_inner_frame.columnconfigure(col, minsize=self.original_column_widths[col] * 8)
        
        # Display history
        for row_idx, entry in enumerate(self.submitted_data, start=1):
            for item in entry['inventory_items']:
                for col, (key, value) in enumerate(item.items()):
                    tk.Label(self.history_inner_frame, text=value, font=('Helvetica', 15),
                           borderwidth=1, relief="solid", padx=5, pady=2).grid(row=row_idx, column=col, sticky="ew")

    def search_inventory(self):
        """Search for inventory items based on criteria"""
        inventory_id = self.search_inventory_id.get().strip()
        project_id = self.search_project_id.get().strip()
        product_id = self.search_product_id.get().strip()
        
        # Here you would typically query your database or data source
        # For demo, we'll create some dummy data matching the search
        search_criteria = {
            'inventory_id': inventory_id,
            'project_id': project_id,
            'product_id': product_id
        }
        
        # Create dummy results based on search criteria
        results = [{
            'zone_activity': "Zone 1",
            'sr_no': "1",
            'inventory_id': inventory_id or "INV001",
            'product_id': product_id or "PROD001",
            'project_id': project_id or "PROJ001",
            'inventory': "Sample Inventory",
            'description': "Sample Description",
            'quantity': "1",
            'comments': "Test comment",
            'status': "Active",
            'received_date': datetime.now().strftime("%Y-%m-%d"),
            'received_by': "Admin",
            'check_status': "No",
            'employee_name': "John Doe",
            'location': "Warehouse",
            'project_name': "Test Project",
            'event_date': datetime.now().strftime("%Y-%m-%d")
        }]
        
        # Display results in both tabs
        self.display_search_results(results)
        self.display_edit_results(results)
        self.display_notebook.select(self.search_results_frame)
        
        logger.info(f"Searching inventory with criteria: {search_criteria}")

    def toggle_wrap(self):
        """Toggle between wrapped and original column sizes"""
        if not self.is_wrapped:
            # Calculate max content width for each column
            col_widths = [len(header) for header in self.headers]  # Start with header widths
            
            # Check all entries in each column
            for row in self.table_entries:
                for col, entry in enumerate(row):
                    content = entry.get()
                    if content:
                        col_widths[col] = max(col_widths[col], len(content))
            
            # Apply the new widths with some padding
            for col, width in enumerate(col_widths):
                adjusted_width = min(width + 5, 50)  # Max width of 50 characters
                self.scrollable_input_frame.columnconfigure(col, minsize=adjusted_width * 8)
            
            self.wrap_btn.config(text="Unwrap")
            self.is_wrapped = True
        else:
            # Reset to original widths
            for col in range(len(self.headers)):
                self.scrollable_input_frame.columnconfigure(col, minsize=self.original_column_widths[col] * 8)
            
            self.wrap_btn.config(text="Wrap")
            self.is_wrapped = False
        
        # Force update of the display
        self.scrollable_input_frame.update_idletasks()
        self.input_canvas.configure(scrollregion=self.input_canvas.bbox("all"))

    def toggle_edit_buttons(self):
        """Enable/disable edit buttons based on selection"""
        selected = any(var.get() for var in self.checkbox_vars) if hasattr(self, 'checkbox_vars') else False
        if selected and not self.edit_mode:
            self.edit_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.NORMAL)
        elif self.edit_mode:
            self.edit_btn.config(state=tk.DISABLED)
            self.update_btn.config(state=tk.NORMAL)
            self.delete_btn.config(state=tk.DISABLED)
        else:
            self.edit_btn.config(state=tk.DISABLED)
            self.update_btn.config(state=tk.DISABLED)
            self.delete_btn.config(state=tk.DISABLED)

    def edit_selected(self):
        """Edit the selected item"""
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get()]
        if len(selected_indices) != 1:
            messagebox.showwarning("Warning", "Please select exactly one item to edit")
            return
        
        self.edit_mode = True
        self.toggle_edit_buttons()
        
        # Get the selected item data
        selected_index = selected_indices[0]
        selected_item = {
            'zone_activity': f"Zone {selected_index+1}",
            'sr_no': str(selected_index+1),
            'inventory_id': f"INV{selected_index+1:03d}",
            'product_id': f"PROD{selected_index+1:03d}",
            'project_id': f"PROJ{selected_index+1:03d}",
            'inventory': f"Inventory Item {selected_index+1}",
            'description': f"Description for item {selected_index+1}",
            'quantity': str(selected_index+1),
            'comments': f"Comment {selected_index+1}",
            'status': "Active",
            'received_date': datetime.now().strftime("%Y-%m-%d"),
            'received_by': "Admin",
            'check_status': "No",
            'employee_name': "John Doe",
            'location': "Warehouse",
            'project_name': "Test Project",
            'event_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        # Store the ID of the item being edited
        self.current_edit_id = selected_item['inventory_id']
        
        # Display the item in the input area for editing
        for col, (key, value) in enumerate(selected_item.items()):
            self.table_entries[0][col].delete(0, tk.END)
            self.table_entries[0][col].insert(0, value)
        
        # Switch to the input area
        self.window.focus_set()

    def update_selected(self):
        """Update the edited item"""
        if not self.edit_mode or not self.current_edit_id:
            messagebox.showwarning("Warning", "No item in edit mode")
            return
        
        # Get the updated data from the input fields
        updated_item = {
            'zone_activity': self.table_entries[0][0].get().strip(),
            'sr_no': self.table_entries[0][1].get().strip(),
            'inventory_id': self.table_entries[0][2].get().strip(),
            'product_id': self.table_entries[0][3].get().strip(),
            'project_id': self.table_entries[0][4].get().strip(),
            'inventory': self.table_entries[0][5].get().strip(),
            'description': self.table_entries[0][6].get().strip(),
            'quantity': self.table_entries[0][7].get().strip(),
            'comments': self.table_entries[0][8].get().strip(),
            'status': self.table_entries[0][9].get().strip(),
            'received_date': self.table_entries[0][10].get().strip(),
            'received_by': self.table_entries[0][11].get().strip(),
            'check_status': self.table_entries[0][12].get().strip(),
            'employee_name': self.table_entries[0][13].get().strip(),
            'location': self.table_entries[0][14].get().strip(),
            'project_name': self.table_entries[0][15].get().strip(),
            'event_date': self.table_entries[0][16].get().strip()
        }
        
        # Here you would typically update your database or data source
        messagebox.showinfo("Success", f"Item {self.current_edit_id} updated successfully")
        logger.info(f"Updated item {self.current_edit_id} with data: {updated_item}")
        
        # Reset edit mode
        self.edit_mode = False
        self.current_edit_id = None
        self.toggle_edit_buttons()
        
        # Clear input fields
        for entry in self.table_entries[0]:
            entry.delete(0, tk.END)
        
        # Refresh the display
        self.search_inventory()

    def delete_selected(self):
        """Delete the selected items"""
        selected_indices = [i for i, var in enumerate(self.checkbox_vars) if var.get()]
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one item to delete")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm", f"Delete {len(selected_indices)} selected item(s)?"):
            return
        
        # Here you would typically delete from your database or data source
        messagebox.showinfo("Success", f"Deleted {len(selected_indices)} item(s)")
        logger.info(f"Deleted items at indices: {selected_indices}")
        
        # Refresh the display
        self.search_inventory()

    def submit_form(self):
        """Handle form submission"""
        # Get data from the single row
        item = {
            'zone_activity': self.table_entries[0][0].get().strip(),
            'sr_no': self.table_entries[0][1].get().strip(),
            'inventory_id': self.table_entries[0][2].get().strip(),
            'product_id': self.table_entries[0][3].get().strip(),
            'project_id': self.table_entries[0][4].get().strip(),
            'inventory': self.table_entries[0][5].get().strip(),
            'description': self.table_entries[0][6].get().strip(),
            'quantity': self.table_entries[0][7].get().strip(),
            'comments': self.table_entries[0][8].get().strip(),
            'status': self.table_entries[0][9].get().strip(),
            'received_date': self.table_entries[0][10].get().strip(),
            'received_by': self.table_entries[0][11].get().strip(),
            'check_status': self.table_entries[0][12].get().strip(),
            'employee_name': self.table_entries[0][13].get().strip(),
            'location': self.table_entries[0][14].get().strip(),
            'project_name': self.table_entries[0][15].get().strip(),
            'event_date': self.table_entries[0][16].get().strip()
        }
        
        # Check if at least one field is filled
        if not any(value for value in item.values()):
            messagebox.showwarning("Warning", "Please enter at least one field")
            return
            
        data = {'inventory_items': [item]}
        self.submitted_data.append(data)
        
        # Clear input fields after submission
        for entry in self.table_entries[0]:
            entry.delete(0, tk.END)
        
        # Update submission history display
        self.display_submission_history()
        self.display_notebook.select(self.submission_history_frame)
        
        messagebox.showinfo("Success", "Form submitted successfully")
        logger.info(f"Form submitted: {data}")

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing Damage Inventory window")
        self.window.destroy()
        self.parent.deiconify()  # Show parent window