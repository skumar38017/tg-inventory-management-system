# frontend/app/assignPage/assign_inventory.py
from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from utils.window_utils import maximize_window
from assignPage.headers import create_header_section, update_clock, configure_treeviews
from assignPage.search_inventory import SearchInventorySection
from assignPage.all_assign_inventory import AllAssignedInventorySection
from assignPage.recent_assign import RecentlySubmittedSection
from assignPage.new_inventory import NewInventorySection
from assignPage.footers import FootersSection
from assignPage.button_section import create_button_section
from assignPage.tree_operations import auto_size_columns, bind_column_resize
from assignPage.data_refresh import refresh_all_data

import logging
logger = logging.getLogger(__name__)

class AssignInventoryWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs's Inventory - Assign Inventory To Employee")

        self.window.option_add('*Dialog.msg.font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))

        maximize_window(self.window)
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

    def setup_ui(self):
        """Set up all UI elements"""
        self.window.grid_rowconfigure(5, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        create_header_section(self.window, self.clock_label_ref, "ASSIGN INVENTORY TO EMPLOYEE")
        update_clock(self.clock_label_ref, self.window)
        
        self.search_section = SearchInventorySection(self.window, self)
        self.search_section.create_search_section()
        
        self.new_entry_section = NewInventorySection(self.window, self)
        
        callbacks = {
            'new_entry': self.new_entry_section.new_entry,
            'search': self.search_product
        }
        create_button_section(self.window, callbacks)
        
        content_frame = tk.Frame(self.window)
        content_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        content_frame.grid_rowconfigure(2, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        self.all_assigned_section = AllAssignedInventorySection(self.window, self)
        self.all_assigned_section.create_all_assigned_inventory_section(content_frame)

        self.recent_section = RecentlySubmittedSection(self.window, self)
        self.recent_section.create_recently_submitted_section(content_frame)

        self.new_entry_section.create_new_entry_section(content_frame)

        self.footers_section = FootersSection(self.window, self)
        self.footers_section.create_bottom_buttons()

        self.headers = [
            "ID", "SNo.","Assigned To", "Employee Name", "Inventory ID", "Project ID", "Product ID",
            "Inventory Name", "Description","Quantity", "Status", "Assigned Date", "Submission Date",
            "Purpose/Reason", "Assigned By", "Comments", "Assignment Return Date", "Assignment Barcode" 
        ]
        
        configure_treeviews(self.assigned_tree, self.recent_tree, self.new_entry_tree, self.headers)
        bind_column_resize([self.assigned_tree, self.recent_tree, self.new_entry_tree], self.auto_size_columns_handler)

    def auto_size_columns_handler(self, tree):
        """Handle auto-sizing for specific trees"""
        if hasattr(self, 'assigned_tree') and tree == self.assigned_tree:
            self.all_assigned_section.auto_size_columns(tree)
        elif hasattr(self, 'recent_tree') and tree == self.recent_tree:
            self.recent_section.auto_size_columns(tree)
        else:
            auto_size_columns(tree, self.headers)

    def refresh_assigned_inventory_list(self):
        self.all_assigned_section.refresh_assigned_inventory_list()

    def load_recent_submissions(self):
        self.recent_section.load_recent_submissions()

    def search_product(self):
        self.search_section.search_product()

    def clear_form(self):
        self.new_entry_section.clear_all_entries()

    def refresh_all_data(self):
        refresh_all_data(self.all_assigned_section, self.recent_section)

    def on_close(self):
        logger.info("Closing Assign Inventory window")
        self.window.destroy()
        self.parent.deiconify()
