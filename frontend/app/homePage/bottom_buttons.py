from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def create_bottom_frames(root, open_to_event, open_from_event, open_assign_inventory, open_damage_inventory, quit_application):
    """Create the bottom frames with modern styled action buttons"""
    bottom_frame = tk.Frame(root, bg='#34495e', relief='raised', bd=2)
    bottom_frame.grid(row=3, column=0, sticky='ew', padx=3, pady=3)
    bottom_frame.grid_columnconfigure(0, weight=1)
    
    button_container = tk.Frame(bottom_frame, bg='#34495e')
    button_container.pack(fill='x', padx=12, pady=8)
    
    left_buttons_frame = tk.Frame(button_container, bg='#34495e')
    left_buttons_frame.pack(side='left', fill='x', expand=True)
    
    buttons = [
        ("To Event", open_to_event, '#2c3e50'),
        ("From Event", open_from_event, '#34495e'),
        ("Assigned", open_assign_inventory, '#7f8c8d'),
        ("Damage/Waste", open_damage_inventory, '#95a5a6')
    ]
    
    for text, command, color in buttons:
        btn = tk.Button(
            left_buttons_frame,
            text=text,
            command=command,
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_large, 'bold'),
            width=15,
            height=2,
            bg=color,
            fg='white',
            relief='flat',
            activebackground=color,
            activeforeground='white'
        )
        btn.pack(side='left', padx=3, fill='x', expand=True)
    
    quit_button = tk.Button(button_container, text="Quit", command=quit_application,
                          font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_large, 'bold'), width=8, height=2,
                          bg='#95a5a6', fg='white', relief='flat',
                          activebackground='#7f8c8d', activeforeground='white')
    quit_button.pack(side='right', padx=5)
