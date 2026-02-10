from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def create_action_buttons(button_frame, callbacks):
    """Create all action buttons"""
    tk.Button(button_frame, text="New", command=callbacks['new'],
             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Submit", command=callbacks['submit'],
             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Edit", command=callbacks['edit'],
             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Update", command=callbacks['update'],
             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Delete", command=callbacks['delete'],
             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Refresh", command=callbacks['refresh'],
             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Return to Main", command=callbacks['close'],
             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold')).pack(side=tk.RIGHT, padx=5)
