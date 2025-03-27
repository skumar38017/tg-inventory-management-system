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
        
        logger.info("Return From Event window opened successfully")

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
               text="ASSIGN INVENTORY TO EMPLOYEE",
               font=('Helvetica', 12, 'bold')).pack()

        # Information fields in row 3
        info_frame = tk.Frame(self.window)
        info_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Employee Name and Location
        tk.Label(info_frame, text="Inventory ID", font=('Helvetica', 9)).grid(row=0, column=0, sticky='e', padx=5)
        self.inventory_id = tk.Entry(info_frame, font=('Helvetica', 9), width=20)
        self.inventory_id.grid(row=0, column=1, sticky='w', padx=5)
        
        tk.Label(info_frame, text="Project ID", font=('Helvetica', 9)).grid(row=0, column=2, sticky='e', padx=5)
        self.project_id = tk.Entry(info_frame, font=('Helvetica', 9), width=20)
        self.project_id.grid(row=0, column=3, sticky='w', padx=5)
        
        # Client Name and Setup Date
        tk.Label(info_frame, text="Product ID", font=('Helvetica', 9)).grid(row=1, column=0, sticky='e', padx=5)
        self.product_id = tk.Entry(info_frame, font=('Helvetica', 9), width=20)
        self.product_id.grid(row=1, column=1, sticky='w', padx=5)
                
        #  add Search button
        search_btn = tk.Button(info_frame, text="Search", command=self.search_product)
        search_btn.grid(row=1, column=2, sticky='e', padx=5)
        
        # Separator line
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # Inventory table in row 5 - using a container frame
        self.table_container = tk.Frame(self.window)
        self.table_container.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        # Create header frame (fixed at top)
        self.header_frame = tk.Frame(self.table_container)
        self.header_frame.pack(side="top", fill="x")

        # Create canvas and scrollbars for content
        self.canvas = tk.Canvas(self.table_container)
        self.v_scrollbar = ttk.Scrollbar(self.table_container, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.table_container, orient="horizontal", command=self.canvas.xview)

        # Pack the widgets
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure scrolling
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Table headers
        self.headers = [
            "Assigned To", "Zone/Activity", "Sr. No.", "InventoryID", "ProductID","ProjectID", "Description/Specifications",
            "Qty","Status", "Purpose/Reason", "Assigned Date", "Submission Date", "Assigned By", 
            "Comments"
        ]

        # Store original column widths
        self.original_column_widths = [15, 20, 10, 15, 15, 25, 10, 15, 20, 15, 15, 15, 20]
        
        # Create headers in header frame
        for col, header in enumerate(self.headers):
            tk.Label(self.header_frame, text=header, font=('Helvetica', 9, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")
            self.header_frame.grid_columnconfigure(col, minsize=self.original_column_widths[col]*8)

        # Create entry fields in scrollable frame
        self.table_entries = []
        for row in range(5):  # Create 5 empty rows
            row_entries = []
            for col in range(len(self.headers)):
                entry = tk.Entry(self.scrollable_frame, font=('Helvetica', 9), 
                               width=self.original_column_widths[col])
                entry.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                self.scrollable_frame.grid_columnconfigure(col, minsize=self.original_column_widths[col]*8)
                row_entries.append(entry)
            self.table_entries.append(row_entries)

        # Function to sync horizontal scrolling between headers and content
        def sync_horizontal_scroll(*args):
            # Move both the canvas and header frame
            self.canvas.xview(*args)
            # Calculate the horizontal offset
            x_offset = -self.canvas.canvasx(0)
            # Apply the same offset to the header frame
            self.header_frame.place(x=x_offset, relwidth=1)
            
        # Configure the horizontal scrollbar to use our sync function
        self.h_scrollbar.config(command=sync_horizontal_scroll)

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
            self.header_frame.grid_columnconfigure(col, minsize=adjusted_width * 8)
            
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.xview_moveto(0)

    def reset_columns(self):
        """Reset columns to their original widths"""
        for col, width in enumerate(self.original_column_widths):
            adjusted_width = width * 8  # Convert character width to pixels
            self.scrollable_frame.grid_columnconfigure(col, minsize=adjusted_width)
            self.header_frame.grid_columnconfigure(col, minsize=adjusted_width)
            
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.xview_moveto(0)

    def add_table_row(self):
        """Add a new row to the table"""
        current_rows = len(self.table_entries)
        row_entries = []
        for col in range(len(self.headers)):
            entry = tk.Entry(self.scrollable_frame, font=('Helvetica', 9), 
                           width=self.original_column_widths[col])
            entry.grid(row=current_rows, column=col, sticky="ew", padx=2, pady=2)
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
                'assigned_to': row[0].get(),
                'zone_activity': row[1].get(),
                'sr_no': row[2].get(),
                'inventory_id': row[3].get(),
                'project_id': row[4].get(),
                'description': row[5].get(),
                'quantity': row[6].get(),
                'status': row[7].get(),
                'purpose': row[8].get(),
                'assigned_date': row[9].get(),
                'submission_date': row[10].get(),
                'assigned_by': row[11].get(),
                'comments': row[12].get()
            }
            data['inventory_items'].append(item)
        
        messagebox.showinfo("Success", "Form submitted successfully")
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