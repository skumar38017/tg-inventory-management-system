from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def create_header_section(window, clock_label_ref):
    """Create header section with clock, company info, and title"""
    # Clock section
    clock_frame = tk.Frame(window)
    clock_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=0)
    clock_frame.grid_columnconfigure(0, weight=1)
    clock_frame.grid_columnconfigure(1, weight=0)
    clock_frame.grid_columnconfigure(2, weight=1)

    clock_label = tk.Label(clock_frame, font=(universal_font_box_size.qr_barcode_header_font_family, 14, 'bold'))
    clock_label.grid(row=0, column=1, sticky='n', pady=(0,0))
    clock_label_ref['label'] = clock_label

    # Company info
    company_frame = tk.Frame(window)
    company_frame.grid(row=1, column=0, columnspan=2, sticky="e", padx=10, pady=0)
    company_frame.grid_columnconfigure(0, weight=1)

    company_info = """Tagglabs Experiential Pvt. Ltd.
        Sector 49, Gurugram, Haryana 122018
        201, Second Floor, Eros City Square Mall
        Eros City Square
        098214 43358"""

    company_label = tk.Label(company_frame,
                           text=company_info,
                           font=(universal_font_box_size.qr_barcode_header_font_family, 12),
                           justify=tk.RIGHT)
    company_label.grid(row=0, column=1, sticky='ne', pady=(0,0))

    # Title section
    title_frame = tk.Frame(window)
    title_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
    
    tk.Label(title_frame, 
           text="Tagglabs Experiential Pvt. Ltd",
           font=(universal_font_box_size.qr_barcode_header_font_family, 14, 'bold')).pack()
    
    tk.Label(title_frame, 
           text="To Create Event Inventory List",
           font=(universal_font_box_size.qr_barcode_header_font_family, 12, 'bold')).pack()

def update_clock(clock_label_ref, window):
    """Update the clock display"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'label' in clock_label_ref:
        clock_label_ref['label'].config(text=now)
    window.after(1000, lambda: update_clock(clock_label_ref, window))
