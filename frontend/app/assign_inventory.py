import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, ttk
from datetime import datetime
import platform
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .api_request.assign_inventory_api_request import (
    search_assigned_inventory_by_id,
    load_submitted_assigned_inventory,
    submit_assigned_inventory,
    show_all_assigned_inventory_from_db,
    update_assigned_inventory,
    get_assigned_inventory_by_id
)

logger = logging.getLogger(__name__)

class AssignInventoryWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs's Inventory - Assign Inventory To Employee")

        # Track edit state
        self.currently_editing_id = None
        self.edit_mode = False
        
        # Track wrap state
        self.is_wrapped = False
        self.original_column_widths = []
        
        # Hide parent window (optional)
        self.parent.withdraw()
        
        # Setup the window
        self.setup_ui()
        self.setup_listbox_bindings()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Focus on this window
        self.window.focus_set()
        
        # Maximize window
        self.maximize_window()
        
        # Load initial data
        self.refresh_assigned_inventory_list()
        
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

    def setup_listbox_bindings(self):
        """Setup double-click binding for list box"""
        self.list_box.bind('<Double-1>', self.on_list_item_double_click)

    def on_list_item_double_click(self, event):
        """Handle double-click on list box item to load for editing"""
        selection = self.list_box.curselection()
        if not selection:
            return
            
        selected_index = selection[0]
        selected_item = self.list_box.get(selected_index)
        
        try:
            # Extract ID from the displayed text
            record_id = selected_item.split("ID:")[1].split("|")[0].strip()
            record_data = get_assigned_inventory_by_id(record_id)
            
            if record_data:
                self.load_record_for_editing(record_data)
        except Exception as e:
            logger.error(f"Error loading record for editing: {e}")
            messagebox.showerror("Error", "Could not load record for editing")

    def load_record_for_editing(self, record_data: Dict):
        """Load record data into the form for editing"""
        self.clear_form()
        self.currently_editing_id = record_data.get('id')
        self.edit_mode = True
        
        # Update search fields
        self.inventory_id.insert(0, record_data.get('inventory_id', ''))
        self.project_id.insert(0, record_data.get('project_id', ''))
        self.product_id.insert(0, record_data.get('product_id', ''))
        self.employee_name.insert(0, record_data.get('employee_name', ''))
        
        # Update table entries
        if self.table_entries:
            row = self.table_entries[0]
            row[0].insert(0, record_data.get('assigned_to', ''))        # Assigned To
            row[1].insert(0, record_data.get('employee_name', ''))      # Employee Name
            row[2].insert(0, record_data.get('zone_activity', ''))     # Zone/Activity
            row[3].insert(0, record_data.get('sr_no', ''))            # Sr. No.
            row[4].insert(0, record_data.get('inventory_id', ''))      # InventoryID
            row[5].insert(0, record_data.get('product_id', ''))        # ProductID
            row[6].insert(0, record_data.get('project_id', ''))        # ProjectID
            row[7].insert(0, record_data.get('inventory_name', ''))    # Inventory Name
            row[8].insert(0, record_data.get('description', ''))       # Description
            row[9].insert(0, record_data.get('quantity', ''))         # Qty
            row[10].insert(0, record_data.get('status', ''))           # Status
            row[11].insert(0, record_data.get('purpose', ''))          # Purpose/Reason
            row[12].insert(0, record_data.get('assigned_date', ''))    # Assigned Date
            row[13].insert(0, record_data.get('submission_date', '')) # Submission Date
            row[14].insert(0, record_data.get('assigned_by', ''))     # Assigned By
            row[15].insert(0, record_data.get('comments', ''))         # Comments
            row[16].insert(0, record_data.get('assignment_returned_date', '')) # Return Date
        
        self.submit_btn.config(text="Update", command=self.update_record)

    def clear_form(self):
        """Clear all form fields"""
        self.inventory_id.delete(0, tk.END)
        self.project_id.delete(0, tk.END)
        self.product_id.delete(0, tk.END)
        self.employee_name.delete(0, tk.END)
        
        for row in self.table_entries:
            for entry in row:
                entry.delete(0, tk.END)
        
        self.currently_editing_id = None
        self.edit_mode = False
        self.submit_btn.config(text="Assign", command=self.submit_form)

    def update_record(self):
        """Handle updating an existing record"""
        if not self.currently_editing_id:
            messagebox.showwarning("Warning", "No record selected for update")
            return
            
        # Validate required fields
        required_fields = [
            self.inventory_id.get(),
            self.project_id.get(),
            self.product_id.get()
        ]
        
        if not all(required_fields):
            messagebox.showwarning("Warning", "Please fill in all required fields")
            return
            
        # Prepare the update data
        update_data = {
            'inventory_id': self.inventory_id.get(),
            'project_id': self.project_id.get(),
            'product_id': self.product_id.get(),
            'assignments': []
        }
        
        for row in self.table_entries:
            assignment = {
                'assigned_to': row[0].get(),
                'employee_name': row[1].get(),
                'zone_activity': row[2].get(),
                'sr_no': row[3].get(),
                'inventory_id': row[4].get(),
                'product_id': row[5].get(),
                'project_id': row[6].get(),
                'inventory_name': row[7].get(),
                'description': row[8].get(),
                'quantity': row[9].get(),
                'status': row[10].get(),
                'purpose': row[11].get(),
                'assigned_date': row[12].get(),
                'submission_date': row[13].get(),
                'assigned_by': row[14].get(),
                'comments': row[15].get(),
                'assignment_returned_date': row[16].get()
            }
            update_data['assignments'].append(assignment)
        
        try:
            success = update_assigned_inventory(self.currently_editing_id, update_data)
            if success:
                messagebox.showinfo("Success", "Record updated successfully")
                logger.info(f"Record {self.currently_editing_id} updated")
                self.refresh_assigned_inventory_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to update record")
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            messagebox.showerror("Error", f"Failed to update record: {str(e)}")

    def refresh_assigned_inventory_list(self):
        """Refresh the list with a proper table view and dynamic column sizing"""
        try:
            # Clear existing content
            for widget in self.list_frame.winfo_children():
                widget.destroy()

            # Configure Treeview style
            style = ttk.Style()
            style.configure('Treeview', 
                        rowheight=15,
                        font=('Helvetica', 9))
            style.map('Treeview', 
                    background=[('selected', '#347083')],
                    foreground=[('selected', 'white')])

            inventory_list = show_all_assigned_inventory_from_db()
            if not inventory_list:
                tk.Label(self.list_frame, 
                        text="No assigned inventory found",
                        font=('Helvetica', 9)).pack(expand=True)
                return

            # Define the fields to display (in order)
            fields = [
                'id', 'assigned_to', 'inventory_id', 'project_id',
                'product_id', 'employee_name', 'inventory_name', 'quantity',
                'status', 'assigned_date', 'sr_no', 'purpose_reason',
                'submission_date', 'assign_by', 'comment',
                'assignment_return_date'
            ]

            # Field name mappings (backend -> display)
            field_mappings = {
                'purpose_reason': 'Purpose',
                'assign_by': 'Assigned By',
                'comment': 'Comments',
                'assignment_return_date': 'Return Date'
            }

            # Calculate column widths
            col_widths = {}
            for field in fields:
                display_name = field_mappings.get(field, field.replace('_', ' ').title())
                col_widths[field] = len(display_name)  # Start with header width

            # Find maximum width for each column
            for item in inventory_list:
                for field in fields:
                    value = str(item.get(field, 'N/A'))
                    col_widths[field] = max(col_widths[field], len(value))

            # Add padding and set minimum width
            for field in col_widths:
                col_widths[field] = max(col_widths[field] + 2, 10)  # Minimum width of 10

            # Create Treeview widget
            tree = ttk.Treeview(self.list_frame, 
                            columns=fields, 
                            show='headings',
                            selectmode='browse')  # Single item selection

            # Configure scrollbars
            vsb = ttk.Scrollbar(self.list_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(self.list_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

            # Grid layout
            tree.grid(row=0, column=0, sticky='nsew')
            vsb.grid(row=0, column=1, sticky='ns')
            hsb.grid(row=1, column=0, sticky='ew')

            # Configure row/column weights
            self.list_frame.grid_rowconfigure(0, weight=1)
            self.list_frame.grid_columnconfigure(0, weight=1)

            # Set up columns with proper display names
            for field in fields:
                display_name = field_mappings.get(field, field.replace('_', ' ').title())
                tree.heading(field, text=display_name)
                tree.column(field, 
                        width=col_widths[field] * 8,  # Adjust multiplier as needed
                        anchor='w')  # Left-align content

            # Add data
            for item in inventory_list:
                values = []
                for field in fields:
                    value = str(item.get(field, 'N/A'))
                    # Format dates if needed
                    if field in ['assigned_date', 'submission_date', 'assignment_return_date'] and value != 'N/A':
                        try:
                            value = value.split('T')[0]  # Just show date part
                        except:
                            pass
                    values.append(value)
                tree.insert('', 'end', values=values)

            # Bind double-click event
            tree.bind('<Double-1>', self.on_tree_item_double_click)

            # Auto-size columns after data is loaded
            self.auto_size_columns(tree, fields)

        except Exception as e:
            logger.error(f"Error refreshing inventory list: {e}")
            messagebox.showerror("Error", "Could not refresh inventory list")
            # Create error label if table fails
            tk.Label(self.list_frame, 
                    text="Error loading inventory data",
                    fg='red',
                    font=('Helvetica', 12)).pack(expand=True)

    def auto_size_columns(self, tree, fields):
        """Automatically adjust column widths based on content"""
        for field in fields:
            tree.column(field, width=0)  # Reset width
            tree.column(field, stretch=True)  # Allow stretching

    def on_tree_item_double_click(self, event):
        """Handle double-click on treeview item"""
        tree = event.widget
        selected = tree.selection()
        
        if not selected:  # No item selected
            return
            
        try:
            item = selected[0]
            values = tree.item(item, 'values')
            if values:  # Check if values exist
                record_id = values[0]  # First column is ID
                record_data = get_assigned_inventory_by_id(record_id)
                if record_data:
                    self.load_record_for_editing(record_data)
        except Exception as e:
            logger.error(f"Error loading record for editing: {e}")
            messagebox.showerror("Error", "Could not load record for editing")

    def on_tree_item_double_click(self, event):
        """Handle double-click on treeview item"""
        tree = event.widget
        selected_items = tree.selection()
        
        # Check if any item is actually selected
        if not selected_items:
            return
            
        try:
            item = selected_items[0]  # Get first selected item
            record_id = tree.item(item, 'values')[0]  # First column is ID
            record_data = get_assigned_inventory_by_id(record_id)
            
            if record_data:
                self.load_record_for_editing(record_data)
        except Exception as e:
            logger.error(f"Error loading record for editing: {e}")
            messagebox.showerror("Error", "Could not load record for editing")
    
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
        tk.Label(list_frame, text="Assigned Inventory List", font=('Helvetica', 10, 'bold')).pack(pady=5)
        
        # Create list box with scrollbar
        self.list_frame = tk.Frame(list_frame)
        self.list_frame.pack(fill='both', expand=True)

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
        tk.Label(assigned_to_label_frame, text="Assignment Details", 
                font=('Helvetica', 10, 'bold')).pack()

        # Table headers frame
        self.header_frame = tk.Frame(self.scrollable_area)
        self.header_frame.pack(side="top", fill="x")

        # Table headers
        self.headers = [
            "Assigned To", "Employee Name", "Zone/Activity", "Sr. No.", "InventoryID", "ProductID", "ProjectID", 
            "Inventory Name", "Description/Specifications", "Qty", "Status", "Purpose/Reason", 
            "Assigned Date", "Submission Date", "Assigned By", "Comments", "Assignment Returned Date"
]

        # Store original column widths
        self.original_column_widths = [15, 20, 15, 10, 15, 15, 15, 25, 10, 15, 20, 15, 15, 15, 20, 20, 15]
        
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

        # Submit/Update button
        self.submit_btn = tk.Button(button_frame, text="Assign", command=self.submit_form,
                             font=('Helvetica', 12, 'bold'))
        self.submit_btn.pack(side=tk.LEFT, padx=5)

        # Clear button
        clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_form,
                            font=('Helvetica', 12, 'bold'))
        clear_btn.pack(side=tk.LEFT, padx=5)

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
        
        try:
            results = search_assigned_inventory_by_id(
                inventory_id=inventory_id,
                project_id=project_id,
                product_id=product_id,
                employee_name=employee_name
            )
            
            if results:
                for item in results:
                    display_text = f"{item.get('InventoryID', 'N/A')} | {item.get('Inventory Name', 'N/A')} | {item.get('Assigned To', 'N/A')}"
                    self.list_box.insert(tk.END, display_text)
            else:
                messagebox.showinfo("Info", "No matching records found")
        except Exception as e:
            logger.error(f"Error during search: {e}")
            messagebox.showerror("Error", "Failed to perform search")

    def submit_form(self):
        """Handle form submission for new records"""
        # Validate required fields
        required_fields = [
            self.inventory_id.get(),
            self.project_id.get(),
            self.product_id.get()
        ]
        
        if not all(required_fields):
            messagebox.showwarning("Warning", "Please fill in all required fields")
            return
            
        # Process the data
        data = {
            'employee_name': self.employee_name.get(),
            'inventory_id': self.inventory_id.get(),
            'assignments': []
        }
        
        for row in self.table_entries:
            item = {
                'assigned_to': row[0].get(),
                'product_id': row[1].get(),
                'zone_activity': row[2].get(),
                'sr_no': row[3].get(),
                'inventory_id': row[4].get(),
                'product_id': row[5].get(),
                'project_id': row[6].get(),
                'inventory_name': row[7].get(),
                'description': row[8].get(),
                'quantity': row[9].get(),
                'status': row[10].get(),
                'purpose': row[11].get(),
                'assigned_date': row[12].get(),
                'submission_date': row[13].get(),
                'assigned_by': row[14].get(),
                'comments': row[15].get(),
                'assignment_returned_date': row[16].get(),
                'project_id': row[17].get(),
            }
            data['assignments'].append(item)
        
        try:
            success = submit_assigned_inventory(data)
            if success:
                messagebox.showinfo("Success", "Assignment submitted successfully")
                logger.info("New assignment submitted")
                self.refresh_assigned_inventory_list()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to submit assignment")
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            messagebox.showerror("Error", f"Failed to submit assignment: {str(e)}")

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing Assign Inventory window")
        self.window.destroy()
        self.parent.deiconify()