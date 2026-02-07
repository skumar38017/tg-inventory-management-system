from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def create_pagination_frame(root, page_info_label_ref, page_entry_ref, go_to_first_page, go_prev_page, go_next_page, go_to_page_from_entry):
    """Create pagination controls between display list and bottom buttons"""
    pagination_frame = tk.Frame(root, bg='#ecf0f1', height=60, relief='raised', bd=1)
    pagination_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=5)
    pagination_frame.grid_propagate(False)
    
    page_info_label = tk.Label(
        pagination_frame,
        text="Page 0 | 20 items per page",
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_small),
        bg='#ecf0f1', fg='#2c3e50'
    )
    page_info_label.pack(side="left", padx=20, pady=15)
    page_info_label_ref['label'] = page_info_label
    
    nav_frame = tk.Frame(pagination_frame, bg='#ecf0f1')
    nav_frame.pack(side="right", padx=20, pady=10)
    
    first_btn = tk.Button(
        nav_frame,
        text="<<",
        command=go_to_first_page,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_medium, 'bold'),
        width=4, height=1,
        bg='#95a5a6', fg='white', relief='flat', bd=1,
        activebackground='#7f8c8d', activeforeground='white'
    )
    first_btn.pack(side="left", padx=3)
    
    prev_btn = tk.Button(
        nav_frame,
        text="<",
        command=go_prev_page,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_medium, 'bold'),
        width=4, height=1,
        bg='#3498db', fg='white', relief='flat', bd=1,
        activebackground='#2980b9', activeforeground='white'
    )
    prev_btn.pack(side="left", padx=3)
    
    page_entry = tk.Entry(
        nav_frame,
        width=6,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_medium),
        justify='center', relief='solid', bd=1
    )
    page_entry.pack(side="left", padx=5)
    page_entry.insert(0, "0")
    page_entry.bind('<Return>', lambda e: go_to_page_from_entry())
    page_entry_ref['entry'] = page_entry
    
    next_btn = tk.Button(
        nav_frame,
        text=">",
        command=go_next_page,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_medium, 'bold'),
        width=4, height=1,
        bg='#3498db', fg='white', relief='flat', bd=1,
        activebackground='#2980b9', activeforeground='white'
    )
    next_btn.pack(side="left", padx=3)
