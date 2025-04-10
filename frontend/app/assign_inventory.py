import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta, date
import logging
from tkinter import font
import uuid
import os
import platform
from typing import Dict, List
from .api_request.assign_inventory_api_request import (
    search_assigned_inventory_by_id,
    load_submitted_assigned_inventory,
    submit_assigned_inventory,
    show_all_assigned_inventory_from_db,
    update_assigned_inventory,
    get_assigned_inventory_by_id,
    delete_assigned_inventory
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
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Focus on this window
        self.window.focus_set()
        
        # Maximize window
        self.maximize_window()
        
        # Load initial data
        self.refresh_assigned_inventory_list()
        self.load_recent_submissions()
        
        logger.info("Assign Inventory window opened successfully")

    def maximize_window(self):
        """Maximize the window based on platform"""
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
        # Configure grid weights for the window
        self.window.grid_rowconfigure(5, weight=1)  # Main content area
        self.window.grid_columnconfigure(0, weight=1)
        
        # Header section - Clock in row 0
        clock_frame = tk.Frame(self.window)
        clock_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=0)
        
        # Clock in center
        self.clock_label = tk.Label(clock_frame, font=('Helvetica', 10))
        self.clock_label.pack()
        self.update_clock()

        # Company info in row 1 (right-aligned)
        company_frame = tk.Frame(self.window)
        company_frame.grid(row=1, column=0, columnspan=2, sticky="e", padx=10, pady=0)
        
        company_info = """Tagglabs Experiential Pvt. Ltd.
Sector 49, Gurugram, Haryana 122018
201, Second Floor, Eros City Square Mall
Eros City Square
098214 43358"""
        
        company_label = tk.Label(company_frame, text=company_info, 
                               font=('Helvetica', 8), justify=tk.RIGHT)
        company_label.pack()

        # Title section in row 2
        title_frame = tk.Frame(self.window)
        title_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Centered company name
        tk.Label(title_frame, text="Tagglabs Experiential Pvt. Ltd",
               font=('Helvetica', 16, 'bold')).pack()
        
        # Centered inventory list title
        tk.Label(title_frame, text="ASSIGN INVENTORY TO EMPLOYEE",
               font=('Helvetica', 14, 'bold')).pack()

        # Search fields in row 3
        search_frame = tk.Frame(self.window)
        search_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Inventory ID
        tk.Label(search_frame, text="Inventory ID:", font=('Helvetica', 10)).grid(row=0, column=0, sticky='e', padx=5)
        self.inventory_id = tk.Entry(search_frame, font=('Helvetica', 10), width=20)
        self.inventory_id.grid(row=0, column=1, sticky='w', padx=5)
        
        # Project ID
        tk.Label(search_frame, text="Project ID:", font=('Helvetica', 10)).grid(row=0, column=2, sticky='e', padx=5)
        self.project_id = tk.Entry(search_frame, font=('Helvetica', 10), width=20)
        self.project_id.grid(row=0, column=3, sticky='w', padx=5)
        
        # Product ID
        tk.Label(search_frame, text="Product ID:", font=('Helvetica', 10)).grid(row=0, column=4, sticky='e', padx=5)
        self.product_id = tk.Entry(search_frame, font=('Helvetica', 10), width=20)
        self.product_id.grid(row=0, column=5, sticky='w', padx=5)
        
        # Employee Name
        tk.Label(search_frame, text="Employee Name:", font=('Helvetica', 10)).grid(row=0, column=6, sticky='e', padx=5)
        self.employee_name = tk.Entry(search_frame, font=('Helvetica', 10), width=20)
        self.employee_name.grid(row=0, column=7, sticky='w', padx=5)
        
        # Search button
        search_btn = tk.Button(search_frame, text="Search", command=self.search_product, 
                             font=('Helvetica', 10))
        search_btn.grid(row=0, column=8, sticky='e', padx=5)

        # New Entry button
        new_entry_btn = tk.Button(search_frame, text="New Entry", command=self.new_entry,
                                font=('Helvetica', 10))
        new_entry_btn.grid(row=0, column=9, sticky='e', padx=5)

        # Separator line
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # =============================================
        # MAIN CONTENT AREA (row 5)
        # =============================================
        content_frame = tk.Frame(self.window)
        content_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        content_frame.grid_rowconfigure(2, weight=1)  # New Entry section
        content_frame.grid_columnconfigure(0, weight=1)

        # ALL ASSIGNED INVENTORY section
        assigned_frame = tk.LabelFrame(content_frame, text="ALL ASSIGNED INVENTORY", 
                                     font=('Helvetica', 10, 'bold'))
        assigned_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        assigned_frame.grid_columnconfigure(0, weight=1)
        assigned_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview for assigned inventory
        self.assigned_tree = ttk.Treeview(assigned_frame)
        self.assigned_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        assigned_vsb = ttk.Scrollbar(assigned_frame, orient="vertical", command=self.assigned_tree.yview)
        assigned_hsb = ttk.Scrollbar(assigned_frame, orient="horizontal", command=self.assigned_tree.xview)
        self.assigned_tree.configure(yscrollcommand=assigned_vsb.set, xscrollcommand=assigned_hsb.set)
        assigned_vsb.grid(row=0, column=1, sticky="ns")
        assigned_hsb.grid(row=1, column=0, sticky="ew")

        # RECENTLY SUBMITTED section
        recent_frame = tk.LabelFrame(content_frame, text="RECENTLY SUBMITTED (current day)", 
                                   font=('Helvetica', 10, 'bold'))
        recent_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        recent_frame.grid_columnconfigure(0, weight=1)
        recent_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview for recent submissions
        self.recent_tree = ttk.Treeview(recent_frame)
        self.recent_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        recent_vsb = ttk.Scrollbar(recent_frame, orient="vertical", command=self.recent_tree.yview)
        recent_hsb = ttk.Scrollbar(recent_frame, orient="horizontal", command=self.recent_tree.xview)
        self.recent_tree.configure(yscrollcommand=recent_vsb.set, xscrollcommand=recent_hsb.set)
        recent_vsb.grid(row=0, column=1, sticky="ns")
        recent_hsb.grid(row=1, column=0, sticky="ew")

        # NEW ENTRY section
        new_entry_frame = tk.LabelFrame(content_frame, text="NEW ENTRY", 
                                    font=('Helvetica', 10, 'bold'))
        new_entry_frame.grid(row=2, column=0, sticky="nsew")
        new_entry_frame.grid_columnconfigure(0, weight=1)
        new_entry_frame.grid_rowconfigure(0, weight=1)  # For the treeview
        new_entry_frame.grid_rowconfigure(1, weight=0)  

        # Treeview for new entries
        self.new_entry_tree = ttk.Treeview(new_entry_frame)
        self.new_entry_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        new_entry_vsb = ttk.Scrollbar(new_entry_frame, orient="vertical", command=self.new_entry_tree.yview)
        new_entry_hsb = ttk.Scrollbar(new_entry_frame, orient="horizontal", command=self.new_entry_tree.xview)
        self.new_entry_tree.configure(yscrollcommand=new_entry_vsb.set, xscrollcommand=new_entry_hsb.set)
        new_entry_vsb.grid(row=0, column=1, sticky="ns")
        new_entry_hsb.grid(row=1, column=0, sticky="ew")
            
        # Action buttons frame for the new entry section
        action_frame = tk.Frame(new_entry_frame)
        action_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)

        # Edit button
        edit_btn = tk.Button(action_frame, text="Edit", command=self.edit_selected_entry,
                            font=('Helvetica', 10))
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Update button
        update_btn = tk.Button(action_frame, text="Update", command=self.update_selected_entry,
                            font=('Helvetica', 10))
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_btn = tk.Button(action_frame, text="Delete", command=self.delete_selected_entry,
                            font=('Helvetica', 10))
        delete_btn.pack(side=tk.LEFT, padx=5)

        # Create a canvas for horizontal scrolling
        entry_canvas = tk.Canvas(new_entry_frame)
        entry_canvas.grid(row=1, column=0, sticky="nsew")
        
        # Add horizontal scrollbar
        entry_hsb = ttk.Scrollbar(new_entry_frame, orient="horizontal", command=entry_canvas.xview)
        entry_hsb.grid(row=2, column=0, sticky="ew")
        entry_canvas.configure(xscrollcommand=entry_hsb.set)
        
        # Create a frame inside the canvas for the entry fields
        self.entry_frame = tk.Frame(entry_canvas)
        entry_canvas.create_window((0, 0), window=self.entry_frame, anchor="nw")
        
        # Configure the entry frame to update scrollregion
        def on_frame_configure(event):
            entry_canvas.configure(scrollregion=entry_canvas.bbox("all"))
        self.entry_frame.bind("<Configure>", on_frame_configure)

        # Define headers for all sections
        self.headers = [
            "ID", "Assigned To", "Employee Name", "Inventory ID", "Project ID", "Product ID",
            "Inventory Name", "Quantity", "Status", "Assigned Date", "Submission Date",
            "Purpose/Reason", "Comments", "Return Date"
        ]
        
        # Configure all treeviews
        self.configure_treeviews()
        
        # Create input fields in the entry frame
        self.create_input_fields()

        # Bottom buttons in row 6
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Wrap button
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

        # Return button
        return_btn = tk.Button(button_frame, text="Return to Main", command=self.on_close,
                             font=('Helvetica', 12, 'bold'))
        return_btn.pack(side=tk.RIGHT, padx=5)

    def configure_treeviews(self):
        """Configure columns for all treeviews including the new entry tree"""
        default_font = font.nametofont("TkDefaultFont")
        
        # Configure all three treeviews
        for tree in [self.assigned_tree, self.recent_tree, self.new_entry_tree]:
            tree['columns'] = self.headers
            tree['show'] = 'headings'  # Remove empty first column
            
            for col, header in enumerate(self.headers):
                tree.heading(col, text=header, anchor='w')
                tree.column(col, width=default_font.measure(header) + 20, 
                        stretch=True, anchor='w')
        
        # Bind double-click events
        self.assigned_tree.bind('<Double-1>', lambda e: self.load_selected_to_new_entry(self.assigned_tree))
        self.recent_tree.bind('<Double-1>', lambda e: self.load_selected_to_new_entry(self.recent_tree))
        
        # Bind column resize events
        for tree in [self.assigned_tree, self.recent_tree, self.new_entry_tree]:
            tree.bind("<Map>", lambda e: self.auto_size_columns(e.widget))

    def load_selected_to_new_entry(self, source_tree):
        """Load selected item from source tree into new entry tree"""
        selected_item = source_tree.selection()
        if not selected_item:
            return
            
        try:
            item = selected_item[0]
            values = source_tree.item(item, 'values')
            
            # Clear existing entries in new entry tree
            self.new_entry_tree.delete(*self.new_entry_tree.get_children())
            
            # Add the selected record to new entry tree
            self.new_entry_tree.insert('', 'end', values=values)
            
            # Store the ID of the record being edited
            self.currently_editing_id = values[0]
            
        except Exception as e:
            logger.error(f"Error loading record to new entry: {e}")
            messagebox.showerror("Error", "Could not load record to new entry")


    def edit_selected_entry(self):
        """Enable editing of the selected entry in new entry tree"""
        selected_item = self.new_entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to edit")
            return
        
        # Get all column values
        item = selected_item[0]
        values = self.new_entry_tree.item(item, 'values')
        
        # Create a top-level edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Record")
        
        # Create entry fields for each column
        entry_widgets = []
        for i, (header, value) in enumerate(zip(self.headers, values)):
            tk.Label(edit_window, text=header).grid(row=i, column=0, padx=5, pady=2)
            entry = tk.Entry(edit_window)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry_widgets.append(entry)
        
        # Save button
        save_btn = tk.Button(edit_window, text="Save Changes",
                            command=lambda: self.save_edited_entry(entry_widgets, edit_window))
        save_btn.grid(row=len(self.headers), column=0, columnspan=2, pady=5)


    def save_edited_entry(self, entry_widgets, edit_window):
        """Save the edited entry back to the new entry tree"""
        try:
            # Get all edited values
            edited_values = [entry.get() for entry in entry_widgets]
            
            # Update the record in new entry tree
            selected_item = self.new_entry_tree.selection()
            if selected_item:
                self.new_entry_tree.item(selected_item[0], values=edited_values)
            
            # Close the edit window
            edit_window.destroy()
            
        except Exception as e:
            logger.error(f"Error saving edited entry: {e}")
            messagebox.showerror("Error", "Failed to save edited entry")

    def update_selected_entry(self):
        """Update the selected entry in the database"""
        selected_item = self.new_entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to update")
            return
        
        if not self.currently_editing_id:
            messagebox.showwarning("Warning", "No record selected for update")
            return
            
        try:
            # Get the updated values
            item = selected_item[0]
            values = self.new_entry_tree.item(item, 'values')
            
            # Prepare the update data
            update_data = {
                'id': values[0],
                'assigned_to': values[1],
                'employee_name': values[2],
                'inventory_id': values[3],
                'project_id': values[4],
                'product_id': values[5],
                'inventory_name': values[6],
                'quantity': values[7],
                'status': values[8],
                'assigned_date': values[9],
                'submission_date': values[10],
                'purpose_reason': values[11],
                'comment': values[12],
                'assignment_return_date': values[13]
            }
            
            # Call the API to update
            success = update_assigned_inventory(self.currently_editing_id, update_data)
            if success:
                messagebox.showinfo("Success", "Record updated successfully")
                self.refresh_assigned_inventory_list()
                self.load_recent_submissions()
            else:
                messagebox.showerror("Error", "Failed to update record")
                
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            messagebox.showerror("Error", f"Failed to update record: {str(e)}")

    def delete_selected_entry(self):
        """Delete the selected entry from the database"""
        selected_item = self.new_entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return
        
        if not self.currently_editing_id:
            messagebox.showwarning("Warning", "No record selected for deletion")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            try:
                # Call the API to delete
                success = delete_assigned_inventory(self.currently_editing_id)
                if success:
                    messagebox.showinfo("Success", "Record deleted successfully")
                    self.new_entry_tree.delete(selected_item)
                    self.refresh_assigned_inventory_list()
                    self.load_recent_submissions()
                else:
                    messagebox.showerror("Error", "Failed to delete record")
                    
            except Exception as e:
                logger.error(f"Error deleting record: {e}")
                messagebox.showerror("Error", f"Failed to delete record: {str(e)}")

    def create_input_fields(self):
        """Create input fields in the entry frame"""
        # Clear any existing widgets
        for widget in self.entry_frame.winfo_children():
            widget.destroy()
        
        # Create header row
        for col, header in enumerate(self.headers):
            if header == "ID":
                continue  # Skip ID column for input
            tk.Label(self.entry_frame, text=header, font=('Helvetica', 10, 'bold'),
                   borderwidth=1, relief="solid").grid(row=0, column=col-1, sticky="ew", padx=1, pady=1)
            self.entry_frame.grid_columnconfigure(col-1, minsize=100)
        
        # Create input rows (start with one empty row)
        self.table_entries = []
        self.add_table_row()

    def refresh_assigned_inventory_list(self):
        """Refresh the list of all assigned inventory with proper column sizing"""
        try:
            # Clear existing items
            self.assigned_tree.delete(*self.assigned_tree.get_children())
            
            # Load data from database
            inventory_list = show_all_assigned_inventory_from_db()
            
            if not inventory_list:
                return
            
            # Add items to treeview
            for item in inventory_list:
                values = [
                    item.get('id', ''),
                    item.get('assigned_to', ''),
                    item.get('employee_name', ''),
                    item.get('inventory_id', ''),
                    item.get('project_id', ''),
                    item.get('product_id', ''),
                    item.get('inventory_name', ''),
                    item.get('quantity', ''),
                    item.get('status', ''),
                    self.format_date(item.get('assigned_date', '')),
                    self.format_date(item.get('submission_date', '')),
                    item.get('purpose_reason', ''),
                    item.get('comment', ''),
                    self.format_date(item.get('assignment_return_date', ''))
                ]
                self.assigned_tree.insert('', 'end', values=values)
            
            # Auto-size columns after loading data
            self.auto_size_columns(self.assigned_tree)
                
        except Exception as e:
            logger.error(f"Error refreshing assigned inventory list: {e}")
            messagebox.showerror("Error", "Could not refresh assigned inventory list")

    def auto_size_columns(self, tree):
        """Automatically resize columns to fit content"""
        default_font = font.nametofont("TkDefaultFont")
        
        for col in range(len(self.headers)):
            # Get max width between header and content
            max_width = default_font.measure(self.headers[col])
            
            # Check content width
            for item in tree.get_children():
                item_width = default_font.measure(tree.set(item, col))
                if item_width > max_width:
                    max_width = item_width
            
            # Add some padding and set column width
            tree.column(col, width=max_width + 20)
                             
    def load_recent_submissions(self):
        """Load recently submitted assignments (current day) with proper column sizing"""
        try:
            # Clear existing items
            self.recent_tree.delete(*self.recent_tree.get_children())
            
            # Load data from API
            recent_submissions = load_submitted_assigned_inventory()
            current_day = datetime.now().date()
            
            if not recent_submissions:
                return
            
            # Add items to treeview
            for item in recent_submissions:
                try:
                    updated_at_str = item.get('updated_at', '')
                    if updated_at_str:
                        # Parse date and check if it's today
                        updated_at = datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
                        if updated_at.date() == current_day:
                            values = [
                                item.get('id', ''),
                                item.get('assigned_to', ''),
                                item.get('employee_name', ''),
                                item.get('inventory_id', ''),
                                item.get('project_id', ''),
                                item.get('product_id', ''),
                                item.get('inventory_name', ''),
                                item.get('quantity', ''),
                                item.get('status', ''),
                                self.format_date(item.get('assigned_date', '')),
                                self.format_date(item.get('submission_date', '')),
                                item.get('purpose_reason', ''),
                                item.get('comment', ''),
                                self.format_date(item.get('assignment_return_date', ''))
                            ]
                            self.recent_tree.insert('', 'end', values=values)
                except Exception as e:
                    logger.warning(f"Skipping record due to parsing error: {e}")
                    continue
            
            # Auto-size columns after loading data
            self.auto_size_columns(self.recent_tree)
                    
        except Exception as e:
            logger.error(f"Error loading recent submissions: {e}")
            messagebox.showerror("Error", "Could not load recent submissions")

    def format_date(self, date_str: str) -> str:
        """Format date string for display (handles multiple formats)"""
        if not date_str or date_str == 'N/A':
            return 'N/A'
        
        try:
            # Try ISO format with timezone first
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            except ValueError:
                try:
                    # Try ISO format without microseconds
                    dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
                except ValueError:
                    # Try simple date format
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
            
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return date_str.split('T')[0] if 'T' in date_str else date_str
        
    def load_selected_item(self, tree):
        """Load selected item from tree into form for editing"""
        selected_item = tree.selection()
        if not selected_item:
            return
            
        try:
            item = selected_item[0]
            record_id = tree.item(item, 'values')[0]  # First column is ID
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
        self.inventory_id.delete(0, tk.END)
        self.inventory_id.insert(0, record_data.get('inventory_id', ''))
        
        self.project_id.delete(0, tk.END)
        self.project_id.insert(0, record_data.get('project_id', ''))
        
        self.product_id.delete(0, tk.END)
        self.product_id.insert(0, record_data.get('product_id', ''))
        
        self.employee_name.delete(0, tk.END)
        self.employee_name.insert(0, record_data.get('employee_name', ''))
        
        # Update first row of input fields
        if self.table_entries:
            row = self.table_entries[0]  # First row
            row[0].insert(0, record_data.get('assigned_to', ''))      # Assigned To
            row[1].insert(0, record_data.get('employee_name', ''))    # Employee Name
            row[2].insert(0, record_data.get('inventory_id', ''))     # Inventory ID
            row[3].insert(0, record_data.get('project_id', ''))       # Project ID
            row[4].insert(0, record_data.get('product_id', ''))       # Product ID
            row[5].insert(0, record_data.get('inventory_name', ''))   # Inventory Name
            row[6].insert(0, record_data.get('quantity', ''))         # Quantity
            row[7].insert(0, record_data.get('status', ''))           # Status
            row[8].insert(0, record_data.get('assigned_date', ''))    # Assigned Date
            row[9].insert(0, record_data.get('submission_date', ''))  # Submission Date
            row[10].insert(0, record_data.get('purpose_reason', ''))  # Purpose/Reason
            row[11].insert(0, record_data.get('comment', ''))         # Comments
            row[12].insert(0, record_data.get('assignment_return_date', ''))  # Return Date
        
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

    def new_entry(self):
        """Clear form for new entry"""
        self.clear_form()
        # Keep only one empty row
        while len(self.table_entries) > 1:
            self.remove_table_row()

    def add_table_row(self):
        """Add a new row to the input table"""
        row_num = len(self.table_entries) + 1  # +1 for header row
        row_entries = []
        
        for col in range(len(self.headers)-1):  # Skip ID column
            entry = tk.Entry(self.entry_frame, font=('Helvetica', 10))
            entry.grid(row=row_num, column=col, sticky="ew", padx=1, pady=1)
            row_entries.append(entry)
        
        self.table_entries.append(row_entries)

    def remove_table_row(self):
        """Remove the last row from the input table"""
        if len(self.table_entries) <= 1:
            messagebox.showwarning("Warning", "Cannot remove the last row")
            return
            
        last_row = self.table_entries.pop()
        for entry in last_row:
            entry.destroy()

    def toggle_wrap(self):
        """Toggle between wrapped and original column sizes"""
        if not self.is_wrapped:
            # Adjust columns to fit content
            for tree in [self.assigned_tree, self.recent_tree]:
                for col in range(len(self.headers)):
                    tree.column(col, width=0)  # Reset width
                    tree.column(col, stretch=True)  # Allow stretching
            self.wrap_btn.config(text="Unwrap")
            self.is_wrapped = True
        else:
            # Reset to original column widths
            for tree in [self.assigned_tree, self.recent_tree]:
                for col in range(len(self.headers)):
                    tree.column(col, width=100, stretch=False)
            self.wrap_btn.config(text="Wrap")
            self.is_wrapped = False

    def search_product(self):
        """Handle product search"""
        inventory_id = self.inventory_id.get()
        project_id = self.project_id.get()
        product_id = self.product_id.get()
        employee_name = self.employee_name.get()
        
        try:
            results = search_assigned_inventory_by_id(
                inventory_id=inventory_id,
                project_id=project_id,
                product_id=product_id,
                employee_name=employee_name
            )
            
            if results:
                # Clear existing items
                self.assigned_tree.delete(*self.assigned_tree.get_children())
                
                # Add search results
                for item in results:
                    values = [
                        item.get('id', ''),
                        item.get('assigned_to', ''),
                        item.get('employee_name', ''),
                        item.get('inventory_id', ''),
                        item.get('project_id', ''),
                        item.get('product_id', ''),
                        item.get('inventory_name', ''),
                        item.get('quantity', ''),
                        item.get('status', ''),
                        item.get('assigned_date', ''),
                        item.get('submission_date', ''),
                        item.get('purpose_reason', ''),
                        item.get('comment', ''),
                        item.get('assignment_return_date', '')
                    ]
                    self.assigned_tree.insert('', 'end', values=values)
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
            
        # Prepare the data
        data = {
            'inventory_id': self.inventory_id.get(),
            'project_id': self.project_id.get(),
            'product_id': self.product_id.get(),
            'employee_name': self.employee_name.get(),
            'assignments': []
        }
        
        for row in self.table_entries:
            assignment = {
                'assigned_to': row[0].get(),
                'employee_name': row[1].get(),
                'inventory_id': row[2].get(),
                'project_id': row[3].get(),
                'product_id': row[4].get(),
                'inventory_name': row[5].get(),
                'quantity': row[6].get(),
                'status': row[7].get(),
                'assigned_date': row[8].get(),
                'submission_date': row[9].get(),
                'purpose_reason': row[10].get(),
                'comment': row[11].get(),
                'assignment_return_date': row[12].get()
            }
            data['assignments'].append(assignment)
        
        try:
            success = submit_assigned_inventory(data)
            if success:
                messagebox.showinfo("Success", "Assignment submitted successfully")
                logger.info("New assignment submitted")
                self.refresh_assigned_inventory_list()
                self.load_recent_submissions()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to submit assignment")
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            messagebox.showerror("Error", f"Failed to submit assignment: {str(e)}")

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
            'employee_name': self.employee_name.get(),
            'assignments': []
        }
        
        for row in self.table_entries:
            assignment = {
                'assigned_to': row[0].get(),
                'employee_name': row[1].get(),
                'inventory_id': row[2].get(),
                'project_id': row[3].get(),
                'product_id': row[4].get(),
                'inventory_name': row[5].get(),
                'quantity': row[6].get(),
                'status': row[7].get(),
                'assigned_date': row[8].get(),
                'submission_date': row[9].get(),
                'purpose_reason': row[10].get(),
                'comment': row[11].get(),
                'assignment_return_date': row[12].get()
            }
            update_data['assignments'].append(assignment)
        
        try:
            success = update_assigned_inventory(self.currently_editing_id, update_data)
            if success:
                messagebox.showinfo("Success", "Record updated successfully")
                logger.info(f"Record {self.currently_editing_id} updated")
                self.refresh_assigned_inventory_list()
                self.load_recent_submissions()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to update record")
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            messagebox.showerror("Error", f"Failed to update record: {str(e)}")

    def update_clock(self):
        """Update the clock display"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.window.after(1000, self.update_clock)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing Assign Inventory window")
        self.window.destroy()
        self.parent.deiconify()