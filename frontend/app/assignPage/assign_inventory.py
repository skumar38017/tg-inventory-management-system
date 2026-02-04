# frontend/app/assignPage/assign_inventory.py
from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from assignPage.search_inventory import SearchInventorySection
from assignPage.all_assign_inventory import AllAssignedInventorySection
from assignPage.recent_assign import RecentlySubmittedSection
from assignPage.new_inventory import NewInventorySection
from assignPage.footers import FootersSection
from api_request.assign_inventory_api_request import (
    search_assigned_inventory_by_id,
    load_submitted_assigned_inventory,
    submit_assigned_inventory,
    show_all_assigned_inventory_from_db,
    update_assigned_inventory,
    get_assigned_inventory_by_id,
    delete_assigned_inventory
)

import logging
logger = logging.getLogger(__name__)

class AssignInventoryWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs's Inventory - Assign Inventory To Employee")

        # Configure global messagebox font for consistent appearance across all dialogs
        self.window.option_add('*Dialog.msg.font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))

        # Maximize window
        self.maximize_window()
        
        # Get status options from StatusEnum
        self.status_options = [status.value for status in StatusEnum]

        # Initialize inventory combo box data
        self.inventory_combo_data = []

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
                
        # Load initial data
        self.refresh_assigned_inventory_list()
        self.load_recent_submissions()
        
        logger.info("Assign Inventory window opened successfully")

    def maximize_window(self):
        maximize_window(self.window)

    def setup_ui(self):
        """Set up all UI elements"""
        # Configure grid weights for the window
        self.window.grid_rowconfigure(5, weight=1)  # Main content area
        self.window.grid_columnconfigure(0, weight=1)
        
        # Header section - Clock in row 0
        clock_frame = tk.Frame(self.window)
        clock_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=0)
        
        # Clock in center
        self.clock_label = tk.Label(clock_frame, font=('Helvetica', 15))
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
                                   font=('Helvetica', 15), justify=tk.RIGHT)
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
        
        # Create search section using separate class
        self.search_section = SearchInventorySection(self.window, self)
        self.search_section.create_search_section()
        
        # Create NEW ENTRY section using separate class (before buttons that reference it)
        self.new_entry_section = NewInventorySection(self.window, self)
        

        # Button frame above separator
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Separator in same line as buttons (left side)
        separator = ttk.Separator(button_frame, orient='horizontal')
        separator.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # New Entry button
        new_entry_btn = tk.Button(button_frame, text="New Entry", command=self.new_entry_section.new_entry,
                                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'), 
                                width=universal_font_box_size.search_button_width)
        new_entry_btn.pack(side=tk.RIGHT, padx=2)

        # Search button
        search_btn = tk.Button(button_frame, text="Search", command=self.search_product, 
                             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'), 
                             width=universal_font_box_size.search_button_width)
        search_btn.pack(side=tk.RIGHT, padx=2)
        
        # =============================================
        # MAIN CONTENT AREA (row 5)
        # =============================================
        content_frame = tk.Frame(self.window)
        content_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        content_frame.grid_rowconfigure(2, weight=1)  # New Entry section
        content_frame.grid_columnconfigure(0, weight=1)

        # Create ALL ASSIGNED INVENTORY section using separate class
        self.all_assigned_section = AllAssignedInventorySection(self.window, self)
        self.all_assigned_section.create_all_assigned_inventory_section(content_frame)

        # Create RECENTLY SUBMITTED section using separate class
        self.recent_section = RecentlySubmittedSection(self.window, self)
        self.recent_section.create_recently_submitted_section(content_frame)

        # Create NEW ENTRY section using separate class
        self.new_entry_section = NewInventorySection(self.window, self)
        self.new_entry_section.create_new_entry_section(content_frame)

        # Create bottom buttons using separate class
        self.footers_section = FootersSection(self.window, self)
        self.footers_section.create_bottom_buttons()

        # Define headers for all sections
        self.headers = [
            "ID", "SNo.","Assigned To", "Employee Name", "Inventory ID", "Project ID", "Product ID",
            "Inventory Name", "Description","Quantity", "Status", "Assigned Date", "Submission Date",
            "Purpose/Reason", "Assigned By", "Comments", "Assignment Return Date", "Assignment Barcode" 
        ]
        
        # Configure all treeviews
        self.configure_treeviews()

    def configure_treeviews(self):
        """Configure columns for all treeviews"""
        default_font = font.nametofont("TkDefaultFont")
        
        # Configure all three treeviews
        for tree in [self.assigned_tree, self.recent_tree, self.new_entry_tree]:
            tree['columns'] = self.headers
            tree['show'] = 'headings'  # Remove empty first column
            
            for col, header in enumerate(self.headers):
                tree.heading(col, text=header, anchor='center')
                tree.column(col, width=default_font.measure(header) + 150, 
                        stretch=False, anchor='center')  # Changed anchor to center
        
        # Bind column resize events
        for tree in [self.assigned_tree, self.recent_tree, self.new_entry_tree]:
            tree.bind("<Map>", lambda e: self.auto_size_columns(e.widget))

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

    def refresh_assigned_inventory_list(self):
        """Delegate to the all assigned inventory section"""
        self.all_assigned_section.refresh_assigned_inventory_list()

    def auto_size_columns(self, tree):
        """Automatically resize columns to fit content"""
        # Delegate to all assigned section if it's the assigned tree
        if hasattr(self, 'assigned_tree') and tree == self.assigned_tree:
            self.all_assigned_section.auto_size_columns(tree)
            return
        
        # Delegate to recent section if it's the recent tree
        if hasattr(self, 'recent_tree') and tree == self.recent_tree:
            self.recent_section.auto_size_columns(tree)
            return
            
        # Handle other trees (new_entry_tree)
        default_font = font.nametofont("TkDefaultFont")
        
        for col in range(len(self.headers)):
            # Get max width between header and content
            max_width = default_font.measure(self.headers[col]) + 60
            
            # Check content width
            for item in tree.get_children():
                item_text = tree.set(item, col)
                item_width = default_font.measure(item_text)
                if item_width > max_width:
                    max_width = item_width + 60
            
            # Set column width with increased bounds (250-600 pixels) and no stretching
            tree.column(col, width=max(min(max_width, 750), 400), stretch=False)
                             
    def load_recent_submissions(self):
        """Delegate to the recently submitted section"""
        self.recent_section.load_recent_submissions()

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

    def search_product(self):
        """Delegate to the search inventory section"""
        self.search_section.search_product()

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

    def refresh_all_data(self):
        """Refresh all data in the window"""
        try:
            self.refresh_assigned_inventory_list()
            self.load_recent_submissions()
            messagebox.showinfo("Success", "Data refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            messagebox.showerror("Error", "Failed to refresh data")

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