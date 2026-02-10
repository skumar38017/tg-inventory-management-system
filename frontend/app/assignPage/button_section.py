from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def create_button_section(window, callbacks):
    """Create button section with search and new entry buttons"""
    button_frame = tk.Frame(window)
    button_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
    
    separator = ttk.Separator(button_frame, orient='horizontal')
    separator.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    new_entry_btn = tk.Button(button_frame, text="New Entry", command=callbacks['new_entry'],
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'), 
                            width=universal_font_box_size.search_button_width)
    new_entry_btn.pack(side=tk.RIGHT, padx=2)

    search_btn = tk.Button(button_frame, text="Search", command=callbacks['search'], 
                         font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'), 
                         width=universal_font_box_size.search_button_width)
    search_btn.pack(side=tk.RIGHT, padx=2)
    
    return button_frame
