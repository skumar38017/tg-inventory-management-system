import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import platform
import logging

logger = logging.getLogger(__name__)

class AssignInventoryWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs's Inventory - Assign Inventory To Employee")

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
        
        logger.info("Assign Inventory window opened successfully")

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
        self.clock_label = tk.Label(clock_frame, font=('Helvetica', 10))
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
                               font=('Helvetica', 8),
                               justify=tk.RIGHT)
        company_label.grid(row=0, column=1, sticky='ne', pady=(0,0))

        # Title section in row 2
        title_frame = tk.Frame(self.window)
        title_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Centered company name
        tk.Label(title_frame, 
               text="Tagglabs Experiential Pvt. Ltd",
               font=('Helvetica', 16, 'bold')).pack()
        
        # Centered inventory list title
        tk.Label(title_frame, 
               text="ASSIGN INVENTORY TO EMPLOYEE",
               font=('Helvetica', 14, 'bold')).pack()

        # Information fields in row 3
        info_frame = tk.Frame(self.window)
        info_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Search fields
        tk.Label(info_frame, text="Inventory ID", font=('Helvetica', 10)).grid(row=0, column=0, sticky='e', padx=5)
        self.inventory_id = tk.Entry(info_frame, font=('Helvetica', 10), width=20)
        self.inventory_id.grid(row=0, column=1, sticky='w', padx=5)
        
        tk.Label(info_frame, text="Project ID", font=('Helvetica', 10)).grid(row=0, column=2, sticky='e', padx=5)
        self.project_id = tk.Entry(info_frame, font=('Helvetica', 10), width=20)
        self.project_id.grid(row=0, column=3, sticky='w', padx=5)
        
        tk.Label(info_frame, text="Product ID", font=('Helvetica', 10)).grid(row=0, column=4, sticky='e', padx=5)
        self.product_id = tk.Entry(info_frame, font=('Helvetica', 10), width=20)
        self.product_id.grid(row=0, column=5, sticky='w', padx=5)

        tk.Label(info_frame, text="Employee Name", font=('Helvetica', 10)).grid(row=0, column=6, sticky='e', padx=5)
        self.employee_name = tk.Entry(info_frame, font=('Helvetica', 10), width=20)
        self.employee_name.grid(row=0, column=7, sticky='w', padx=5)

        # Search button
        search_btn = tk.Button(info_frame, text="Search", command=self.search_product, font=('Helvetica', 10))
        search_btn.grid(row=0, column=8, sticky='e', padx=5)

        # Separator line
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # =============================================
        # MAIN CONTENT AREA (2/3 for list, 1/3 for table)
        # =============================================
        content_frame = tk.Frame(self.window)
        content_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        # Configure grid weights for the content frame
        content_frame.grid_rowconfigure(0, weight=2)  # Search results (larger)
        content_frame.grid_rowconfigure(1, weight=1)  # Table (smaller)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # LIST BOX CONTAINER (2/3 of vertical space)
        list_frame = tk.Frame(content_frame, bd=2, relief=tk.GROOVE)
        list_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Add label for the list box
        tk.Label(list_frame, text="Search Results", font=('Helvetica', 10, 'bold')).pack(pady=5)
        
        # Create list box with scrollbar
        self.list_box = tk.Listbox(list_frame, font=('Helvetica', 10))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.list_box.yview)
        self.list_box.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # TABLE CONTAINER (1/3 of vertical space)
        table_container = tk.Frame(content_frame, bd=2, relief=tk.GROOVE)
        table_container.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Create a frame to hold all table elements
        self.table_holder = tk.Frame(table_container)
        self.table_holder.pack(fill="both", expand=True)

        # Create canvas for scrolling
        self.horizontal_canvas = tk.Canvas(self.table_holder)
        self.horizontal_canvas.pack(side="top", fill="both", expand=True)

        # Create scrollable area
        self.scrollable_area = tk.Frame(self.horizontal_canvas)
        self.horizontal_canvas.create_window((0, 0), window=self.scrollable_area, anchor="nw")

        # "Assigned To" label centered above headers
        assigned_to_label_frame = tk.Frame(self.scrollable_area)
        assigned_to_label_frame.pack(side="top", fill="x", pady=(5,0))
        
        # Center the label in its frame
        tk.Label(assigned_to_label_frame, text="Assigned To", 
                font=('Helvetica', 10, 'bold')).pack()

        # Table headers frame
        self.header_frame = tk.Frame(self.scrollable_area)
        self.header_frame.pack(side="top", fill="x")

        # Table headers
        self.headers = [
            "Assigned To", "Zone/Activity", "Sr. No.", "InventoryID", "ProductID", "ProjectID", 
            "Description/Specifications", "Qty", "Status", "Purpose/Reason", 
            "Assigned Date", "Submission Date", "Assigned By", "Comments", "Assignment Returned Date"
        ]

        # Store original column widths
        self.original_column_widths = [15, 20, 10, 15, 15, 15, 25, 10, 15, 20, 15, 15, 15, 20, 20]
        
        # Create headers
        for col, header in enumerate(self.headers):
            tk.Label(self.header_frame, text=header, font=('Helvetica', 10, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")
            self.header_frame.grid_columnconfigure(col, minsize=self.original_column_widths[col]*10)

        # Create vertical scrollable canvas for content
        self.vertical_canvas = tk.Canvas(self.scrollable_area)
        self.vertical_canvas.pack(side="top", fill="both", expand=True)

        # Create scrollable frame for input fields
        self.scrollable_frame = tk.Frame(self.vertical_canvas)
        self.vertical_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.table_holder, orient="vertical", command=self.vertical_canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.horizontal_canvas.xview)
        
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")

        # Configure scrolling
        self.vertical_canvas.configure(yscrollcommand=self.v_scrollbar.set)
        self.horizontal_canvas.configure(xscrollcommand=self.h_scrollbar.set)
        
        # Create input fields
        self.table_entries = []
        for row in range(1):  # Create 1 row for input fields
            row_entries = []
            for col, header in enumerate(self.headers):
                entry = tk.Entry(self.scrollable_frame, font=('Helvetica', 10),
                               width=self.original_column_widths[col])
                entry.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                self.scrollable_frame.grid_columnconfigure(col, minsize=self.original_column_widths[col]*10)
                row_entries.append(entry)
            self.table_entries.append(row_entries)

        # Configure scroll regions
        def update_scroll_region(event):
            self.vertical_canvas.configure(scrollregion=self.vertical_canvas.bbox("all"))
            self.horizontal_canvas.configure(scrollregion=self.horizontal_canvas.bbox("all"))
            
            content_width = self.scrollable_frame.winfo_width()
            header_width = self.header_frame.winfo_width()
            if content_width > header_width:
                self.header_frame.config(width=content_width)
            
        self.scrollable_frame.bind("<Configure>", update_scroll_region)
        self.header_frame.bind("<Configure>", update_scroll_region)

        # Bottom buttons in row 6
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Wrap button to adjust columns (toggle)
        self.wrap_btn = tk.Button(button_frame, text="Wrap", command=self.toggle_wrap,
                                font=('Helvetica', 12, 'bold'))
        self.wrap_btn.pack(side=tk.LEFT, padx=5)

        # Remove row button
        remove_row_btn = tk.Button(button_frame, text="Remove Row", command=self.remove_table_row,
                                 font=('Helvetica', 12, 'bold'))
        remove_row_btn.pack(side=tk.LEFT, padx=5)

        # Add row button
        add_row_btn = tk.Button(button_frame, text="Add Row", command=self.add_table_row,
                              font=('Helvetica', 12, 'bold'))
        add_row_btn.pack(side=tk.LEFT, padx=5)

        # Submit button
        submit_btn = tk.Button(button_frame, text="Assign", command=self.submit_form,
                             font=('Helvetica', 12, 'bold'))
        submit_btn.pack(side=tk.LEFT, padx=5)

        # Return button on right
        return_button = tk.Button(button_frame, 
                                text="Return to Main", 
                                command=self.on_close,
                                font=('Helvetica', 12, 'bold'),
                                width=15)
        return_button.pack(side=tk.RIGHT, padx=5)

        # =============================================
        # Grid configuration for window
        # =============================================
        self.window.grid_rowconfigure(0, weight=0)  # Clock
        self.window.grid_rowconfigure(1, weight=0)  # Company info
        self.window.grid_rowconfigure(2, weight=0)  # Title
        self.window.grid_rowconfigure(3, weight=0)  # Info fields
        self.window.grid_rowconfigure(4, weight=0)  # Separator
        self.window.grid_rowconfigure(5, weight=1)  # Content area (list + table)
        self.window.grid_rowconfigure(6, weight=0)  # Buttons
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

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
        """Adjust column widths based on content for both header and entries"""
        col_widths = [len(header) for header in self.headers]
        
        for row in self.table_entries:
            for col, entry in enumerate(row):
                content = entry.get()
                if content:
                    col_widths[col] = max(col_widths[col], len(content))
        
        for col, width in enumerate(col_widths):
            adjusted_width = min(width + 5, 50) * 10  # Increased multiplier for better spacing
            self.scrollable_frame.grid_columnconfigure(col, minsize=adjusted_width)
            self.header_frame.grid_columnconfigure(col, minsize=adjusted_width)
            
        self.vertical_canvas.configure(scrollregion=self.vertical_canvas.bbox("all"))
        self.horizontal_canvas.configure(scrollregion=self.horizontal_canvas.bbox("all"))
        self.horizontal_canvas.xview_moveto(0)

    def reset_columns(self):
        """Reset columns to their original widths for both header and entries"""
        for col, width in enumerate(self.original_column_widths):
            adjusted_width = width * 10  # Increased multiplier for better spacing
            self.scrollable_frame.grid_columnconfigure(col, minsize=adjusted_width)
            self.header_frame.grid_columnconfigure(col, minsize=adjusted_width)
            
        self.vertical_canvas.configure(scrollregion=self.vertical_canvas.bbox("all"))
        self.horizontal_canvas.configure(scrollregion=self.horizontal_canvas.bbox("all"))
        self.horizontal_canvas.xview_moveto(0)

    def add_table_row(self):
        """Add a new row to the table"""
        current_rows = len(self.table_entries)
        row_entries = []
        for col in range(len(self.headers)):
            entry = tk.Entry(self.scrollable_frame, font=('Helvetica', 10),
                           width=self.original_column_widths[col])
            entry.grid(row=current_rows, column=col, sticky="ew", padx=2, pady=2)
            row_entries.append(entry)
        self.table_entries.append(row_entries)
        self.vertical_canvas.configure(scrollregion=self.vertical_canvas.bbox("all"))
        self.horizontal_canvas.configure(scrollregion=self.horizontal_canvas.bbox("all"))

    def remove_table_row(self):
        """Remove the last row from the table"""
        if len(self.table_entries) <= 1:
            messagebox.showwarning("Warning", "Cannot remove the last row")
            return
            
        last_row = self.table_entries.pop()
        for entry in last_row:
            entry.destroy()
        
        self.vertical_canvas.configure(scrollregion=self.vertical_canvas.bbox("all"))
        self.horizontal_canvas.configure(scrollregion=self.horizontal_canvas.bbox("all"))

    def search_product(self):
        """Handle product search and display results in list box"""
        inventory_id = self.inventory_id.get()
        project_id = self.project_id.get()
        product_id = self.product_id.get()
        employee_name = self.employee_name.get()
        
        # Clear previous results
        self.list_box.delete(0, tk.END)
        
        # Here you would typically implement your search logic
        # For demonstration, we'll add some dummy data
        if inventory_id or project_id or product_id or employee_name:
            # Add some sample results (more items to fill the larger list box)
            for i in range(1, 20):
                result_text = f"Result {i}: "
                if inventory_id:
                    result_text += f"InvID: {inventory_id}-{i} "
                if project_id:
                    result_text += f"ProjID: {project_id}-{i} "
                if product_id:
                    result_text += f"ProdID: {product_id}-{i} "
                if employee_name:
                    result_text += f"Emp: {employee_name}-{i}"
                
                self.list_box.insert(tk.END, result_text.strip())
        else:
            messagebox.showwarning("Warning", "Please enter at least one search criteria")

    def submit_form(self):
        """Handle form submission"""
        # Validate required fields
        required_fields = [
            self.inventory_id.get(),
            self.project_id.get(),
            self.product_id.get()
        ]
        
        if not all(required_fields):
            messagebox.showwarning("Warning", "Please fill in all search fields")
            return
            
        # Process the data
        data = {
            'inventory_id': self.inventory_id.get(),
            'project_id': self.project_id.get(),
            'product_id': self.product_id.get(),
            'assignments': []
        }
        
        for row in self.table_entries:
            item = {
                'assigned_to': row[0].get(),
                'zone_activity': row[1].get(),
                'sr_no': row[2].get(),
                'inventory_id': row[3].get(),
                'product_id': row[4].get(),
                'project_id': row[5].get(),
                'description': row[6].get(),
                'quantity': row[7].get(),
                'status': row[8].get(),
                'purpose': row[9].get(),
                'assigned_date': row[10].get(),
                'submission_date': row[11].get(),
                'assigned_by': row[12].get(),
                'comments': row[13].get(),
                'assignment_returned_date': row[14].get()
            }
            data['assignments'].append(item)
        
        messagebox.showinfo("Success", "Assignment submitted successfully")
        logger.info(f"Form submitted: {data}")

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing Assign Inventory window")
        self.window.destroy()
        self.parent.deiconify()