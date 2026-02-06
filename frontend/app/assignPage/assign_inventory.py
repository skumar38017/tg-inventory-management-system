# frontend/app/assignPage/assign_inventory.py
from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from assignPage.headers import create_header_section, update_clock, configure_treeviews
from assignPage.search_inventory import SearchInventorySection
from assignPage.all_assign_inventory import AllAssignedInventorySection
from assignPage.recent_assign import RecentlySubmittedSection
from assignPage.new_inventory import NewInventorySection
from assignPage.footers import FootersSection
from api_request.assign_inventory_api_request import show_all_assigned_inventory_from_db

import logging
logger = logging.getLogger(__name__)

class AssignInventoryWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs's Inventory - Assign Inventory To Employee")

        self.window.option_add('*Dialog.msg.font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))

        self.maximize_window()
        self.status_options = [status.value for status in StatusEnum]
        self.inventory_combo_data = []
        self.currently_editing_id = None
        self.edit_mode = False
        self.is_wrapped = False
        self.original_column_widths = []
        self.clock_label_ref = {}
        
        self.parent.withdraw()
        self.setup_ui()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.focus_set()
        self.refresh_assigned_inventory_list()
        self.load_recent_submissions()
        
        logger.info("Assign Inventory window opened successfully")

    def maximize_window(self):
        maximize_window(self.window)

    def setup_ui(self):
        """Set up all UI elements"""
        self.window.grid_rowconfigure(5, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Create header section
        create_header_section(self.window, self.clock_label_ref)
        update_clock(self.clock_label_ref, self.window)
        
        # Create search section
        self.search_section = SearchInventorySection(self.window, self)
        self.search_section.create_search_section()
        
        # Create NEW ENTRY section (before buttons)
        self.new_entry_section = NewInventorySection(self.window, self)
        
        # Button frame
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        separator = ttk.Separator(button_frame, orient='horizontal')
        separator.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        new_entry_btn = tk.Button(button_frame, text="New Entry", command=self.new_entry_section.new_entry,
                                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'), 
                                width=universal_font_box_size.search_button_width)
        new_entry_btn.pack(side=tk.RIGHT, padx=2)

        search_btn = tk.Button(button_frame, text="Search", command=self.search_product, 
                             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'), 
                             width=universal_font_box_size.search_button_width)
        search_btn.pack(side=tk.RIGHT, padx=2)
        
        # Main content area
        content_frame = tk.Frame(self.window)
        content_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        content_frame.grid_rowconfigure(2, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Create sections
        self.all_assigned_section = AllAssignedInventorySection(self.window, self)
        self.all_assigned_section.create_all_assigned_inventory_section(content_frame)

        self.recent_section = RecentlySubmittedSection(self.window, self)
        self.recent_section.create_recently_submitted_section(content_frame)

        self.new_entry_section.create_new_entry_section(content_frame)

        self.footers_section = FootersSection(self.window, self)
        self.footers_section.create_bottom_buttons()

        # Define headers
        self.headers = [
            "ID", "SNo.","Assigned To", "Employee Name", "Inventory ID", "Project ID", "Product ID",
            "Inventory Name", "Description","Quantity", "Status", "Assigned Date", "Submission Date",
            "Purpose/Reason", "Assigned By", "Comments", "Assignment Return Date", "Assignment Barcode" 
        ]
        
        # Configure treeviews
        configure_treeviews(self.assigned_tree, self.recent_tree, self.new_entry_tree, self.headers)
        
        # Bind column resize events
        for tree in [self.assigned_tree, self.recent_tree, self.new_entry_tree]:
            tree.bind("<Map>", lambda e: self.auto_size_columns(e.widget))

    def refresh_assigned_inventory_list(self):
        """Delegate to the all assigned inventory section"""
        self.all_assigned_section.refresh_assigned_inventory_list()

    def auto_size_columns(self, tree):
        """Automatically resize columns to fit content"""
        if hasattr(self, 'assigned_tree') and tree == self.assigned_tree:
            self.all_assigned_section.auto_size_columns(tree)
            return
        
        if hasattr(self, 'recent_tree') and tree == self.recent_tree:
            self.recent_section.auto_size_columns(tree)
            return
            
        default_font = font.nametofont("TkDefaultFont")
        
        for col in range(len(self.headers)):
            max_width = default_font.measure(self.headers[col]) + 60
            
            for item in tree.get_children():
                item_text = tree.set(item, col)
                item_width = default_font.measure(item_text)
                if item_width > max_width:
                    max_width = item_width + 60
            
            tree.column(col, width=max(min(max_width, 750), 400), stretch=False)
                             
    def load_recent_submissions(self):
        """Delegate to the recently submitted section"""
        self.recent_section.load_recent_submissions()

    def search_product(self):
        """Delegate to the search inventory section"""
        self.search_section.search_product()

    def clear_form(self):
        """Delegate to the new inventory section"""
        self.new_entry_section.clear_all_entries()

    def refresh_all_data(self):
        """Refresh all data in the window"""
        try:
            self.refresh_assigned_inventory_list()
            self.load_recent_submissions()
            messagebox.showinfo("Success", "Data refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            messagebox.showerror("Error", "Failed to refresh data")

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing Assign Inventory window")
        self.window.destroy()
        self.parent.deiconify()