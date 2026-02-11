from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def create_header_frame(root):
    """Create and configure the header frame with clock and company info"""
    header_frame = tk.Frame(root, bg='#2c3e50', relief='raised', bd=2)
    header_frame.grid(row=0, column=0, sticky="nsew", padx=3, pady=1)
    
    header_frame.grid_columnconfigure(0, weight=1)
    header_frame.grid_rowconfigure(0, weight=1)
    header_frame.grid_rowconfigure(1, weight=1)
    
    global clock_label
    clock_label = tk.Label(header_frame, font=(universal_font_box_size.qr_barcode_header_font_family, 14, 'bold'), 
                          fg='white', bg='#2c3e50')
    clock_label.grid(row=0, column=0, sticky='n', pady=(8,0))
    
    company_info = """Tagglabs Experiential Pvt. Ltd.
        Sector 49, Gurugram, Haryana 122518
        251, Second Floor, Eros City Square Mall
        Eros City Square, 098214 43358"""
    
    global company_label
    company_label = tk.Label(header_frame,
                           text=company_info,
                           font=(universal_font_box_size.qr_barcode_header_font_family, 12),
                           justify='right',
                           anchor='ne',
                           fg='#ecf0f1', bg='#2c3e50')
    company_label.grid(row=1, column=0, sticky='ne', pady=(0,8), padx=12)
    
    return header_frame, clock_label, company_label
