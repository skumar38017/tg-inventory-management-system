# frontend/app/assignPage/search_inventory.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

class SearchInventorySection:
    def __init__(self, parent_window, parent_instance):
        self.window = parent_window
        self.parent = parent_instance
        
    def create_search_section(self):
        """Create the search fields section"""
        #  ----------------------- Search Buttons Header Section -----------------------
        # Search fields in row 3
        search_frame = tk.Frame(self.window)
        search_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Inventory ID
        tk.Label(search_frame, text="Inventory ID:", font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold')).grid(row=0, column=0, sticky='e', padx=5)
        self.parent.inventory_id = tk.Entry(search_frame, font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), width=universal_font_box_size.search_entry_width)
        self.parent.inventory_id.grid(row=0, column=1, sticky='w', padx=5)
        
        # Project ID
        tk.Label(search_frame, text="Project ID:", font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold')).grid(row=0, column=2, sticky='e', padx=5)
        self.parent.project_id = tk.Entry(search_frame, font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), width=universal_font_box_size.search_entry_width)
        self.parent.project_id.grid(row=0, column=3, sticky='w', padx=5)
        
        # Product ID
        tk.Label(search_frame, text="Product ID:", font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold')).grid(row=0, column=4, sticky='e', padx=5)
        self.parent.product_id = tk.Entry(search_frame, font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), width=universal_font_box_size.search_entry_width)
        self.parent.product_id.grid(row=0, column=5, sticky='w', padx=5)
        
        # Employee Name
        tk.Label(search_frame, text="Employee Name:", font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_label_font_size, 'bold')).grid(row=0, column=6, sticky='e', padx=5)
        self.parent.employee_name = tk.Entry(search_frame, font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), width=universal_font_box_size.search_entry_width)
        self.parent.employee_name.grid(row=0, column=7, sticky='w', padx=5)
        
        #  ----------------------- End of Search Buttons Header Section -----------------------
        
        return search_frame
