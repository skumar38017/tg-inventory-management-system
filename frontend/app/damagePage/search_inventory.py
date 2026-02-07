from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from api_request.damage_inventory_api_request import search_wastage_inventory_by_id

def setup_search_ui(parent, search_callback):
    """Setup search UI section"""
    search_frame = tk.LabelFrame(parent, text="Search", padx=5, pady=5,
                               font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    search_frame.pack(fill=tk.X, padx=10, pady=5)
    
    search_entries = {}
    
    tk.Label(search_frame, text="Inventory ID:", 
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=0, column=0, sticky=tk.E, padx=5)
    search_entries['inventory_id'] = tk.Entry(search_frame, width=universal_font_box_size.search_entry_width,
                                      font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                                      justify='center')
    search_entries['inventory_id'].grid(row=0, column=1, sticky=tk.W, padx=5)
    
    tk.Label(search_frame, text="Project ID:",
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=0, column=2, sticky=tk.E, padx=5)
    search_entries['project_id'] = tk.Entry(search_frame, width=universal_font_box_size.search_entry_width,
                                    font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                                    justify='center')
    search_entries['project_id'].grid(row=0, column=3, sticky=tk.W, padx=5)
    
    tk.Label(search_frame, text="Product ID:",
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=0, column=4, sticky=tk.E, padx=5)
    search_entries['product_id'] = tk.Entry(search_frame, width=universal_font_box_size.search_entry_width,
                                    font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                                    justify='center')
    search_entries['product_id'].grid(row=0, column=5, sticky=tk.W, padx=5)
    
    tk.Button(search_frame, text="Search", command=search_callback,
             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=0, column=6, padx=5)
    
    return search_frame, search_entries

def search_inventory(search_entries):
    """Search inventory based on criteria"""
    inventory_id = search_entries['inventory_id'].get().strip()
    project_id = search_entries['project_id'].get().strip()
    product_id = search_entries['product_id'].get().strip()
    
    results = search_wastage_inventory_by_id(
        inventory_id=inventory_id,
        project_id=project_id,
        product_id=product_id
    )
    
    logger.info(f"Search completed with {len(results) if results else 0} results")
    return results