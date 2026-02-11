from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def create_bottom_buttons(window, callbacks):
    """Create bottom button frame with all action buttons"""
    button_frame = tk.Frame(window)
    button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

    wrap_btn = tk.Button(button_frame, text="Wrap", command=callbacks['toggle_wrap'],
                        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    wrap_btn.pack(side=tk.LEFT, padx=5)

    remove_row_btn = tk.Button(button_frame, text="Remove Row", command=callbacks['remove_row'],
                             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    remove_row_btn.pack(side=tk.LEFT, padx=5)

    add_row_btn = tk.Button(button_frame, text="Add Row", command=callbacks['add_row'],
                          font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    add_row_btn.pack(side=tk.LEFT, padx=5)

    submit_btn = tk.Button(button_frame, text="Submit", command=callbacks['submit'],
                         font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    submit_btn.pack(side=tk.LEFT, padx=5)

    return_button = tk.Button(button_frame, 
                            text="Return to Main", 
                            command=callbacks['close'],
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'),
                            width=15)
    return_button.pack(side=tk.RIGHT, padx=5)

    return wrap_btn
