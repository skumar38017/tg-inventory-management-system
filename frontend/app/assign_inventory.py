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
        # TABLE CONTAINER WITH PROPER SCROLLING SOLUTION
        # =============================================
        
        # Main container for the table
        self.table_container = tk.Frame(self.window)
        self.table_container.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        # Create a frame to hold both the header and scrollable content
        self.table_holder = tk.Frame(self.table_container)
        self.table_holder.pack(fill="both", expand=True)

        # Create a canvas for horizontal scrolling that will hold both header and content
        self.horizontal_canvas = tk.Canvas(self.table_holder)
        self.horizontal_canvas.pack(side="top", fill="both", expand=True)

        # Create a frame inside the canvas for the header and content
        self.scrollable_area = tk.Frame(self.horizontal_canvas)
        self.horizontal_canvas.create_window((0, 0), window=self.scrollable_area, anchor="nw")

        # Create header frame (fixed at top)
        self.header_frame = tk.Frame(self.scrollable_area)
        self.header_frame.pack(side="top", fill="x")

        # Create vertical scrollable canvas for content only
        self.vertical_canvas = tk.Canvas(self.scrollable_area)
        self.vertical_canvas.pack(side="top", fill="both", expand=True)

        # Create scrollable frame for content
        self.scrollable_frame = tk.Frame(self.vertical_canvas)
        self.vertical_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(self.table_holder, orient="vertical", command=self.vertical_canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.table_container, orient="horizontal", command=self.horizontal_canvas.xview)
        
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")

        # Configure scrolling
        self.vertical_canvas.configure(yscrollcommand=self.v_scrollbar.set)
        self.horizontal_canvas.configure(xscrollcommand=self.h_scrollbar.set)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.vertical_canvas.configure(
            scrollregion=self.vertical_canvas.bbox("all")))
        
        self.scrollable_area.bind("<Configure>", lambda e: self.horizontal_canvas.configure(
            scrollregion=self.horizontal_canvas.bbox("all")))

        # Table headers
        self.headers = [
            "Assigned To", "Zone/Activity", "Sr. No.", "InventoryID", "ProductID", "ProjectID", 
            "Description/Specifications", "Qty", "Status", "Purpose/Reason", 
            "Assigned Date", "Submission Date", "Assigned By", "Comments"
        ]

        # Store original column widths
        self.original_column_widths = [15, 20, 10, 15, 15, 15, 25, 10, 15, 20, 15, 15, 15, 20]
        
        # Create headers in header frame
        for col, header in enumerate(self.headers):
            tk.Label(self.header_frame, text=header, font=('Helvetica', 10, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")
            self.header_frame.grid_columnconfigure(col, minsize=self.original_column_widths[col]*10)

        # Create entry fields in scrollable frame
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

        # Make sure columns stay aligned
        def update_scroll_region(event):
            # Update vertical scroll region
            self.vertical_canvas.configure(scrollregion=self.vertical_canvas.bbox("all"))
            # Update horizontal scroll region
            self.horizontal_canvas.configure(scrollregion=self.horizontal_canvas.bbox("all"))
            
            # Keep header and content columns aligned
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
        # List Display
        # =============================================
        list_frame = tk.Frame(self.window)
        list_frame.grid(row=9, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        tk.Label(list_frame, text="List Display", font=('Helvetica', 12, 'bold')).pack()

        self.listbox = tk.Listbox(list_frame, font=('Helvetica', 10), width=50, height=15)
        self.listbox.pack(fill="both", expand=True)

        # Add some sample data to the listbox
        for i in range(10):
            self.listbox.insert(tk.END, f"Sample Items {i+1}") 

        # =============================================
        # Grid configuration for window
        # =============================================
        self.window.grid_rowconfigure(0, weight=0)  # Clock
        self.window.grid_rowconfigure(1, weight=0)  # Company info
        self.window.grid_rowconfigure(2, weight=0)  # Title
        self.window.grid_rowconfigure(3, weight=0)  # Info fields
        self.window.grid_rowconfigure(4, weight=0)  # Separator
        self.window.grid_rowconfigure(5, weight=1)  # Table
        self.window.grid_rowconfigure(6, weight=0)  # Buttons
        self.window.grid_rowconfigure(7, weight=1)  # List Display
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
        """Handle product search"""
        inventory_id = self.inventory_id.get()
        project_id = self.project_id.get()
        product_id = self.product_id.get()
        
        # Here you would typically implement your search logic
        # For now, we'll just show a message
        messagebox.showinfo("Search", f"Searching for Inventory ID: {inventory_id}, Project ID: {project_id}, Product ID: {product_id}")

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
                'comments': row[13].get()
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

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = AssignInventoryWindow(root)
    root.mainloop()