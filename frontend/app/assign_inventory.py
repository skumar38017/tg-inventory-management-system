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
            
        # Scrollbars - Modified for proper left-to-right scrolling
        assigned_vsb = ttk.Scrollbar(assigned_frame, orient="vertical", command=self.assigned_tree.yview)
        assigned_hsb = ttk.Scrollbar(assigned_frame, orient="horizontal", command=self.assigned_tree.xview)
        self.assigned_tree.configure(yscrollcommand=assigned_vsb.set, xscrollcommand=assigned_hsb.set)
        
        # Grid placement - ensure horizontal scrollbar is at the bottom
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
        
        # Scrollbars - Modified for proper left-to-right scrolling
        recent_vsb = ttk.Scrollbar(recent_frame, orient="vertical", command=self.recent_tree.yview)
        recent_hsb = ttk.Scrollbar(recent_frame, orient="horizontal", command=self.recent_tree.xview)
        self.recent_tree.configure(yscrollcommand=recent_vsb.set, xscrollcommand=recent_hsb.set)
        
        # Grid placement
        recent_vsb.grid(row=0, column=1, sticky="ns")
        recent_hsb.grid(row=1, column=0, sticky="ew")

        # NEW ENTRY section
        new_entry_frame = tk.LabelFrame(content_frame, text="NEW ENTRY", 
                                    font=('Helvetica', 10, 'bold'))
        new_entry_frame.grid(row=2, column=0, sticky="nsew")
        new_entry_frame.grid_columnconfigure(0, weight=1)
        new_entry_frame.grid_rowconfigure(0, weight=1)  # For the treeview
        
        # Treeview for new entries
        self.new_entry_tree = ttk.Treeview(new_entry_frame)
        self.new_entry_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars - Modified for proper left-to-right scrolling
        new_entry_vsb = ttk.Scrollbar(new_entry_frame, orient="vertical", command=self.new_entry_tree.yview)
        new_entry_hsb = ttk.Scrollbar(new_entry_frame, orient="horizontal", command=self.new_entry_tree.xview)
        self.new_entry_tree.configure(yscrollcommand=new_entry_vsb.set, xscrollcommand=new_entry_hsb.set)
        
        # Grid placement
        new_entry_vsb.grid(row=0, column=1, sticky="ns")
        new_entry_hsb.grid(row=1, column=0, sticky="ew")
            
        # Action buttons frame for the new entry section
        action_frame = tk.Frame(new_entry_frame)
        action_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

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

        # Clear button
        clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_form,
                            font=('Helvetica', 12, 'bold'))
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Return button
        return_btn = tk.Button(button_frame, text="Return to Main", command=self.on_close,
                             font=('Helvetica', 12, 'bold'))
        return_btn.pack(side=tk.RIGHT, padx=5)

        # Define headers for all sections
        self.headers = [
            "ID", "SNo.","Assigned To", "Employee Name", "Inventory ID", "Project ID", "Product ID",
            "Inventory Name", "Description","Quantity", "Status", "Assigned Date", "Submission Date",
            "Purpose/Reason", "Assigned By", "Comments", "Assignment Return Date", "Assignment Barcode" 
        ]
        
        # Configure all treeviews
        self.configure_treeviews()
        
        # Bind double-click events
        self.assigned_tree.bind('<Double-1>', lambda e: self.load_selected_to_new_entry(self.assigned_tree))
        self.recent_tree.bind('<Double-1>', lambda e: self.load_selected_to_new_entry(self.recent_tree))

    def configure_treeviews(self):
        """Configure columns for all treeviews"""
        default_font = font.nametofont("TkDefaultFont")
        
        # Configure all three treeviews
        for tree in [self.assigned_tree, self.recent_tree, self.new_entry_tree]:
            tree['columns'] = self.headers
            tree['show'] = 'headings'  # Remove empty first column
            
            for col, header in enumerate(self.headers):
                tree.heading(col, text=header, anchor='w')
                tree.column(col, width=default_font.measure(header) + 20, 
                        stretch=False, anchor='w')  # Changed stretch to False for better control
        
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
            self.edit_mode = True
            
            # Update search fields
            self.inventory_id.delete(0, tk.END)
            self.inventory_id.insert(0, values[3])  # Inventory ID
            
            self.project_id.delete(0, tk.END)
            self.project_id.insert(0, values[4])  # Project ID
            
            self.product_id.delete(0, tk.END)
            self.product_id.insert(0, values[5])  # Product ID
            
            self.employee_name.delete(0, tk.END)
            self.employee_name.insert(0, values[2])  # Employee Name
                        
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
        
        # List of read-only fields (these won't be editable)
        read_only_fields = ['ID', 'Inventory ID', 'Inventory Name','Project ID', 'Product ID', 'Assigned Date', 'assignment_barcode','Employee Nmae', 'Assigned By']
        
        # Create entry fields for each column
        entry_widgets = []
        for i, (header, value) in enumerate(zip(self.headers, values)):
            tk.Label(edit_window, text=header).grid(row=i, column=0, padx=5, pady=2)
            
            if header in read_only_fields:
                # Create a label for read-only fields
                label = tk.Label(edit_window, text=value, relief="sunken", bg="#f0f0f0")
                label.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
                entry_widgets.append(label)  # Still append to maintain order
            else:
                # Create an entry widget for editable fields
                entry = tk.Entry(edit_window)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
                entry_widgets.append(entry)
        
        # Save button
        save_btn = tk.Button(edit_window, text="Save Changes",
                            command=lambda: self.save_edited_entry(entry_widgets, edit_window))
        save_btn.grid(row=len(self.headers), column=0, columnspan=2, pady=5)
        
        # Make the window resizable
        edit_window.grid_columnconfigure(1, weight=1)

    def save_edited_entry(self, entry_widgets, edit_window):
        """Save the edited entry back to the new entry tree"""
        try:
            # Get all edited values
            edited_values = []
            for i, widget in enumerate(entry_widgets):
                if isinstance(widget, tk.Label):  # Read-only field
                    edited_values.append(widget.cget("text"))
                else:  # Editable field
                    edited_values.append(widget.get())
            
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
        """Update the selected entry in the database using employee_name and inventory_id"""
        selected_item = self.new_entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to update")
            return
        
        try:
            # Get the updated values
            item = selected_item[0]
            values = self.new_entry_tree.item(item, 'values')
            
            # Ensure we have enough values
            if len(values) < 14:
                messagebox.showerror("Error", "Incomplete record data")
                return
                
            # Get the required identifiers from the treeview
            employee_name = values[3]  # Employee Name is at index 3
            inventory_id = values[4]   # Inventory ID is at index 4
            
            if not employee_name or not inventory_id:
                messagebox.showerror("Error", "Employee Name and Inventory ID are required for update")
                return
                
            # Prepare the update data according to API spec
            update_data = {
                'assign_to': values[2] or "",  # Assigned To
                'sno': values[1] or "",  # SNo
                'zone_activity': "",  # zone_activity
                'description': values[8] or "",  # Description
                'quantity': values[9] or "1",  # Quantity
                'status': values[10].lower() if values[10].lower() in ["assigned", "returned"] else "assigned",  # Status
                'purpose_reason': values[13] or "",  # Purpose/Reason
                'comment': values[15] or "",  # Comments
                'submission_date': self.format_api_date(values[12]) or datetime.now().isoformat(),
                'assigned_date': self.format_api_date(values[11]) or datetime.now().strftime('%Y-%m-%d'),
                'assignment_return_date': self.format_api_date(values[16]) or (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
                'employee_name': employee_name,
                'inventory_id': inventory_id
            }
            
            # Call the API to update
            success = update_assigned_inventory(employee_name, inventory_id, update_data)
            if success:
                messagebox.showinfo("Success", "Record updated successfully")
                self.refresh_assigned_inventory_list()
                self.load_recent_submissions()
                self.clear_form()
            else:
                messagebox.showerror("Error", "Failed to update record. Check logs for details.")
                
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            messagebox.showerror("Error", f"Failed to update record: {str(e)}")

    def format_api_date(self, date_str: str) -> str:
        """Format date string for API (convert empty to None)"""
        if not date_str or date_str.strip() in ['', 'N/A', ' ']:
            return None
        try:
            # Try to parse the date in various formats
            for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f%z'):
                try:
                    dt = datetime.strptime(date_str, fmt)
                    if fmt.endswith('%z'):  # Contains timezone info
                        return dt.isoformat()
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return None
        except Exception:
            return None

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
                    self.clear_form()
                else:
                    messagebox.showerror("Error", "Failed to delete record")
                    
            except Exception as e:
                logger.error(f"Error deleting record: {e}")
                messagebox.showerror("Error", f"Failed to delete record: {str(e)}")

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
                    item.get('sno', ''),
                    item.get('assigned_to', ''),
                    item.get('employee_name', ''),
                    item.get('inventory_id', ''),
                    item.get('project_id', ''),
                    item.get('product_id', ''),
                    item.get('inventory_name', ''),
                    item.get('description', ''),
                    item.get('quantity', ''),
                    item.get('status', ''),
                    self.format_date(item.get('assigned_date', '')),
                    self.format_date(item.get('submission_date', '')),
                    item.get('purpose_reason', ''),
                    item.get('assigned_by', ''),
                    item.get('comments', ''),
                    self.format_date(item.get('assignment_return_date', '')),
                    item.get('assignment_barcode', '')
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
            max_width = default_font.measure(self.headers[col]) + 20
            
            # Check content width
            for item in tree.get_children():
                item_text = tree.set(item, col)
                item_width = default_font.measure(item_text)
                if item_width > max_width:
                    max_width = item_width + 20
            
            # Set column width with bounds (100-300 pixels) and no stretching
            tree.column(col, width=max(min(max_width, 300), 100), stretch=False)
                             
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
                                item.get('sno', ''),
                                item.get('assigned_to', ''),
                                item.get('employee_name', ''),
                                item.get('inventory_id', ''),
                                item.get('project_id', ''),
                                item.get('product_id', ''),
                                item.get('inventory_name', ''),
                                item.get('description', ''),
                                item.get('quantity', ''),
                                item.get('status', ''),
                                self.format_date(item.get('assigned_date', '')),
                                self.format_date(item.get('submission_date', '')),
                                item.get('purpose_reason', ''),
                                item.get('assigned_by', ''),
                                item.get('comments', ''),
                                self.format_date(item.get('assignment_return_date', '')),
                                item.get('assignment_barcode', '')
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
        if not date_str or date_str == ' ':
            return ' '
        
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

# --------------------------- New Entry Popup ---------------------------
    def new_entry(self):
        """Create a popup window for new entry registration with proper scrolling"""
        # Create popup window
        popup = tk.Toplevel(self.window)
        popup.title("Register New Assignment")
        popup.geometry("1200x700")  # Larger size for better visibility
        popup.resizable(True, True)
        
        # Make the popup modal
        popup.grab_set()
        
        # Configure grid weights
        popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = tk.Frame(popup)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        tk.Label(header_frame, text="NEW INVENTORY ASSIGNMENT", 
                font=('Helvetica', 14, 'bold')).pack()
        
        # Main content area with improved scrolling
        content_frame = tk.Frame(popup)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Create a canvas and scrollbars
        canvas = tk.Canvas(content_frame, borderwidth=0, highlightthickness=0)
        vsb = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        hsb = ttk.Scrollbar(content_frame, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        canvas.grid(row=0, column=0, sticky="nsew")
        
        # Frame inside canvas
        table_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=table_frame, anchor="nw")
        
        # Define headers
        headers = [
            "SNo.", "Assigned To", "Employee Name", "Inventory ID", "Project ID", 
            "Product ID", "Inventory Name", "Description", "Quantity", "Status", 
            "Assigned Date", "Purpose/Reason", "Assigned By", "Comments", 
            "Assignment Return Date"
        ]
        
        # Create Treeview with custom style
        style = ttk.Style()
        style.configure("Treeview", 
                      rowheight=25, 
                      font=('Helvetica', 10),
                      highlightthickness=1,
                      highlightcolor="#4CAF50",
                      highlightbackground="#4CAF50")
        style.map("Treeview", 
                background=[('selected', '#4CAF50')],
                foreground=[('selected', 'white')])
        
        tree = ttk.Treeview(table_frame, columns=headers, show="headings", height=15, selectmode="extended")
        tree.pack(fill="both", expand=True)
        
        # Configure columns with initial widths
        col_widths = {
            "SNo.": 50,
            "Assigned To": 120,
            "Employee Name": 150,
            "Inventory ID": 120,
            "Project ID": 100,
            "Product ID": 100,
            "Inventory Name": 150,
            "Description": 200,
            "Quantity": 70,
            "Status": 100,
            "Assigned Date": 120,
            "Purpose/Reason": 200,
            "Assigned By": 120,
            "Comments": 200,
            "Assignment Return Date": 150
        }
        
        for col in headers:
            tree.heading(col, text=col, anchor='w')
            tree.column(col, width=col_widths.get(col, 120), anchor='w', stretch=False)
        
        # Add sample data row
        tree.insert("", "end", values=[""] * len(headers))
        
        # Function to auto-resize columns
        def auto_resize_columns():
            font = tk.font.Font()
            for col in headers:
                max_width = font.measure(col) + 20  # Header width
                
                # Check all rows for content width
                for item in tree.get_children():
                    cell_value = tree.set(item, col)
                    cell_width = font.measure(cell_value) + 20
                    if cell_width > max_width:
                        max_width = cell_width
                
                # Set column width with reasonable limits
                tree.column(col, width=min(max(max_width, col_widths.get(col, 120)), 300))
        
        # Make cells editable with highlighting
        def on_double_click(event):
            region = tree.identify("region", event.x, event.y)
            if region == "cell":
                column = tree.identify_column(event.x)
                item = tree.identify_row(event.y)
                
                # Highlight the cell being edited
                tree.selection_set(item)
                tree.focus(item)
                tree.focus_set()
                
                # Get column info
                col_index = int(column[1:]) - 1
                col_name = headers[col_index]
                
                # Get current value
                current_value = tree.set(item, column)
                
                # Create entry widget with matching style
                entry = ttk.Entry(table_frame, 
                                font=('Helvetica', 10),
                                style="Treeview")
                entry.insert(0, current_value)
                entry.select_range(0, tk.END)
                entry.focus()
                
                def save_edit():
                    tree.set(item, column, entry.get())
                    entry.destroy()
                    auto_resize_columns()  # Resize after edit
                
                entry.bind("<Return>", lambda e: save_edit())
                entry.bind("<FocusOut>", lambda e: save_edit())
                
                # Place the entry widget exactly over the cell
                x, y, width, height = tree.bbox(item, column)
                entry.place(x=x, y=y, width=width, height=height)
        
        tree.bind("<Double-1>", on_double_click)
        
        # Highlight row on selection
        def on_select(event):
            for item in tree.selection():
                tree.focus(item)
        
        tree.bind("<<TreeviewSelect>>", on_select)
        
        # Button frame
        button_frame = tk.Frame(popup)
        button_frame.grid(row=2, column=0, sticky="e", padx=10, pady=10)
        
        # Add Row button
        add_row_btn = tk.Button(button_frame, text="Add Row",
                              command=lambda: [tree.insert("", "end", values=[""] * len(headers)), auto_resize_columns()],
                              font=('Helvetica', 10))
        add_row_btn.pack(side=tk.LEFT, padx=5)
        
        # Remove Row button
        remove_row_btn = tk.Button(button_frame, text="Remove Row",
                                 command=lambda: [tree.delete(tree.selection()), auto_resize_columns()],
                                 font=('Helvetica', 10))
        remove_row_btn.pack(side=tk.LEFT, padx=5)
        
        # Submit button
        submit_btn = tk.Button(button_frame, text="Submit",
                             command=lambda: self.submit_new_entry(popup, tree, headers),
                             font=('Helvetica', 10, 'bold'), bg="#4CAF50", fg="white")
        submit_btn.pack(side=tk.RIGHT, padx=5)
        
        # Clear button
        clear_btn = tk.Button(button_frame, text="Clear",
                            command=lambda: [tree.delete(item) for item in tree.get_children()],
                            font=('Helvetica', 10))
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Back button
        back_btn = tk.Button(button_frame, text="Back",
                           command=popup.destroy,
                           font=('Helvetica', 10))
        back_btn.pack(side=tk.RIGHT, padx=5)
        
        # Update scrollregion when size changes
        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        table_frame.bind("<Configure>", update_scrollregion)
        
        # Initial auto-resize of columns
        auto_resize_columns()

    def submit_new_entry(self, popup, tree, headers):
        """Submit the new entry form data"""
        items = tree.get_children()
        if not items:
            messagebox.showwarning("Warning", "No items to submit")
            return
        
        data = {'assignments': []}
        
        for item in items:
            values = tree.item(item, 'values')
            if not any(values):  # Skip empty rows
                continue
                
            assignment = dict(zip(headers, values))
            
            # Convert to expected API format
            formatted_data = {
                'sno': assignment.get("SNo.", ""),
                'assigned_to': assignment.get("Assigned To", ""),
                'employee_name': assignment.get("Employee Name", ""),
                'inventory_id': assignment.get("Inventory ID", ""),
                'project_id': assignment.get("Project ID", ""),
                'product_id': assignment.get("Product ID", ""),
                'inventory_name': assignment.get("Inventory Name", ""),
                'description': assignment.get("Description", ""),
                'quantity': assignment.get("Quantity", "1"),
                'status': assignment.get("Status", "Assigned"),
                'assigned_date': assignment.get("Assigned Date", datetime.now().strftime('%Y-%m-%d')),
                'purpose_reason': assignment.get("Purpose/Reason", ""),
                'assigned_by': assignment.get("Assigned By", ""),
                'comments': assignment.get("Comments", ""),
                'assignment_return_date': assignment.get("Assignment Return Date", 
                                                       (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')),
                'zone_activity': " "
            }
            data['assignments'].append(formatted_data)
        
        try:
            # Show loading indicator
            popup.config(cursor="watch")
            popup.update()
            
            success = submit_assigned_inventory(data)
            if success:
                messagebox.showinfo("Success", f"{len(data['assignments'])} assignment(s) submitted successfully")
                self.refresh_assigned_inventory_list()
                self.load_recent_submissions()
                popup.destroy()
            else:
                messagebox.showerror("Error", "Failed to submit assignment(s)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit assignment(s): {str(e)}")
        finally:
            popup.config(cursor="")

#  ----------------------- End of New Entry Popup -----------------------

    def add_table_row(self):
        """Add a new row to the input table in the new entry tree with auto-generated ID"""
        # Generate default values for a new row
        default_values = [
            ""  # Auto-generated short  ID
            "",  # SNo
            "",  # Assigned To
            self.employee_name.get() or "",  # Employee Name
            self.inventory_id.get() or "",  # Inventory ID
            self.project_id.get() or "",  # Project ID
            self.product_id.get() or "",  # Product ID
            "",  # Inventory Name
            "",  # Description
            "1",  # Default quantity
            "Assigned",  # Default status
            datetime.now().strftime('%Y-%m-%d'),  # Assigned Date
            datetime.now().strftime('%Y-%m-%d'),  # Submission Date
            "",  # Purpose/Reason
            "",  # Assigned By
            "",  # Comments
            (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
            ""  # Assignment Barcode
        ]
        
        # Add the new row to the treeview
        self.new_entry_tree.insert('', 'end', values=default_values)

    def remove_table_row(self):
        """Remove the selected row from the input table"""
        selected_item = self.new_entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a row to remove")
            return
            
        self.new_entry_tree.delete(selected_item)

    def toggle_wrap(self):
        """Toggle between wrapped and original column sizes"""
        if not self.is_wrapped:
            # Adjust columns to fit content
            for tree in [self.assigned_tree, self.recent_tree, self.new_entry_tree]:
                for col in range(len(self.headers)):
                    tree.column(col, width=0)  # Reset width
                    tree.column(col, stretch=True)  # Allow stretching
            self.wrap_btn.config(text="Unwrap")
            self.is_wrapped = True
        else:
            # Reset to original column widths
            for tree in [self.assigned_tree, self.recent_tree, self.new_entry_tree]:
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
                        self.format_date(item.get('assigned_date', '')),
                        self.format_date(item.get('submission_date', '')),
                        self.get('assigned_by', ''),
                        self.get('comments', ''),
                        self.format_date(self.get('assignment_return_date', '')),
                        self.get('assignment_barcode', ''),
                        item.get('purpose_reason', ''),
                    ]
                    self.assigned_tree.insert('', 'end', values=values)
            else:
                messagebox.showinfo("Info", "No matching records found")
        except Exception as e:
            logger.error(f"Error during search: {e}")
            messagebox.showerror("Error", "Failed to perform search")

    def submit_form(self):
        """Handle form submission for new records - all fields are optional"""
        # Get all items from the new entry tree
        items = self.new_entry_tree.get_children()
        if not items:
            messagebox.showwarning("Warning", "No items to submit")
            return
            
        # Prepare the data
        data = {
            'inventory_id': self.inventory_id.get() or " ",
            'project_id': self.project_id.get() or " ",
            'product_id': self.product_id.get() or " ",
            'employee_name': self.employee_name.get() or " ",
            'assignments': []
        }
        
        for item in items:
            values = list(self.new_entry_tree.item(item, 'values'))
                            
            assignment = {
                'ID':  " ", # Default value if not provided
                'sno': values[1] or " ",
                'assigned_to': values[2] or "",
                'employee_name': values[3] or "",
                'inventory_id': values[4] or "",
                'project_id': values[5] or " ",
                'product_id': values[6] or " ",
                'inventory_name': values[7] or " ",
                'description': values[8] or " ",
                'quantity': values[9] or "1",  # Default quantity
                'status': values[10] or "Assigned",  # Default status
                'assigned_date': values[11] or datetime.now().strftime('%Y-%m-%d'),
                'submission_date': " ", # Default value if not provided
                'purpose_reason': values[13] or " ",
                'assigned_by': values[14] or " ",
                'comments': values[15] or " ",
                'assignment_return_date': values[16] or (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
                'zone_activity': " "  # Default value if not provided
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

    def submit_selected_entry(self):
        """Handle submission of selected entry (for edit mode)"""
        if self.edit_mode:
            self.update_selected_entry()
        else:
            self.submit_form()

    def clear_form(self):
        """Clear all form fields"""
        self.inventory_id.delete(0, tk.END)
        self.project_id.delete(0, tk.END)
        self.product_id.delete(0, tk.END)
        self.employee_name.delete(0, tk.END)
        self.new_entry_tree.delete(*self.new_entry_tree.get_children())
        
        self.currently_editing_id = None
        self.edit_mode = False

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