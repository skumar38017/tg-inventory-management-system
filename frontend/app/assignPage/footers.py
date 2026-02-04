# frontend/app/assignPage/footers.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

class FootersSection:
    def __init__(self, parent_window, parent_instance):
        self.window = parent_window
        self.parent = parent_instance
        
    def create_bottom_buttons(self):
        """Create the bottom buttons section"""
        # Bottom buttons in row 6
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        # Wrap button
        self.parent.wrap_btn = tk.Button(button_frame, text="Wrap", command=self.parent.new_entry_section.toggle_wrap,
                                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'),
                                width=universal_font_box_size.button_width)
        self.parent.wrap_btn.pack(side=tk.LEFT, padx=2)

        # Remove row button
        remove_row_btn = tk.Button(button_frame, text="Remove Row", command=self.parent.new_entry_section.remove_table_row,
                                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'),
                                 width=universal_font_box_size.button_width)
        remove_row_btn.pack(side=tk.LEFT, padx=2)

        # Add row button
        add_row_btn = tk.Button(button_frame, text="Add Row", command=self.parent.new_entry_section.add_table_row,
                              font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'),
                              width=universal_font_box_size.button_width)
        add_row_btn.pack(side=tk.LEFT, padx=2)

        # Clear button
        clear_btn = tk.Button(button_frame, text="Clear", command=self.parent.clear_form,
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size),
                            width=universal_font_box_size.button_width)
        clear_btn.pack(side=tk.LEFT, padx=2)

        # Return button
        return_btn = tk.Button(button_frame, text="Return", command=self.parent.on_close,
                             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'),
                             width=universal_font_box_size.button_width)
        return_btn.pack(side=tk.RIGHT, padx=5)

        # Refresh button (moved to right side)
        refresh_btn = tk.Button(button_frame, text="Refresh", command=self.parent.refresh_all_data,
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size),
                            width=universal_font_box_size.button_width)
        refresh_btn.pack(side=tk.RIGHT, padx=2)

        return button_frame
