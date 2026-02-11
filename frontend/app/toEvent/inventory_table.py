from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def create_inventory_table(window, parent_instance):
    """Create inventory table with canvas and scrollbars"""
    table_frame = tk.Frame(window)
    table_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(table_frame)
    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=canvas.xview)
    h_scrollbar.pack(side="bottom", fill="x")

    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    canvas.yview_moveto(0)

    headers = [
        "Zone/Activity", "Sr. No.", "Inventory", "Description",
        "Quantity", "Comments", "Total", "Units", "Per Unit Power (W)",
        "Total Power (W)", "Status", "POC", "RecQty"
    ]

    original_column_widths = [20 if col not in [4,6,7,8,9] else 15 for col in range(len(headers))]
    
    for col, header in enumerate(headers):
        tk.Label(scrollable_frame, text=header, 
               font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'),
               borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")

    return canvas, scrollable_frame, headers, original_column_widths

def add_table_row(scrollable_frame, table_entries, headers, original_column_widths, status_options, canvas):
    """Add a new row to the table"""
    current_rows = len(table_entries)
    
    row_entries = []
    for col in range(len(headers)):
        if col == 2:  # Inventory column
            combo_frame = tk.Frame(scrollable_frame)
            combo_frame.grid(row=current_rows+1, column=col, sticky="ew", padx=2, pady=2)
            
            combo = InventoryComboBox(combo_frame)
            combo.configure(font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                          height=universal_font_box_size.search_entry_font_size,
                          justify='center')
            combo.pack(fill=tk.X, expand=True)
            row_entries.append(combo)
        elif col == 10:  # Status column
            status_var = tk.StringVar()
            combo = ttk.Combobox(
                scrollable_frame,
                textvariable=status_var,
                values=status_options,
                state="readonly",
                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                justify='center'
            )
            combo.set(status_options[0])
            combo.grid(row=current_rows+1, column=col, sticky="ew", padx=2, pady=2)
            
            # Set dropdown list font
            combo.option_add('*TCombobox*Listbox.font', 
                           (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
            
            row_entries.append(combo)
        else:
            entry = tk.Entry(scrollable_frame, 
                        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                        width=original_column_widths[col],
                        justify='center')
            if col == 12:  # RecQty column
                entry.config(state='readonly')
            entry.grid(row=current_rows+1, column=col, sticky="ew", padx=2, pady=2)
            row_entries.append(entry)
    table_entries.append(row_entries)
    
    canvas.configure(scrollregion=canvas.bbox("all"))

def remove_table_row(table_entries, canvas):
    """Remove the last row from the table"""
    if len(table_entries) <= 1:
        messagebox.showwarning("Warning", "Cannot remove the last row")
        return
        
    last_row = table_entries.pop()
    for entry in last_row:
        entry.destroy()
    
    canvas.configure(scrollregion=canvas.bbox("all"))

def clear_table(table_entries):
    """Clear all table entries except the first row"""
    while len(table_entries) > 1:
        last_row = table_entries.pop()
        for entry in last_row:
            entry.destroy()
    
    if table_entries:
        for entry in table_entries[0]:
            entry.delete(0, tk.END)

def toggle_wrap(is_wrapped, wrap_btn, headers, scrollable_frame, table_entries, canvas):
    """Toggle between wrapped and original column sizes"""
    if not is_wrapped:
        adjust_columns(headers, scrollable_frame, table_entries, canvas)
        wrap_btn.config(text="Unwrap")
        return True
    else:
        reset_columns([20 if col not in [4,6,7,8,9] else 15 for col in range(len(headers))], 
                     scrollable_frame, canvas)
        wrap_btn.config(text="Wrap")
        return False

def adjust_columns(headers, scrollable_frame, table_entries, canvas):
    """Adjust column widths based on content"""
    col_widths = [len(header) for header in headers]
    
    for row in table_entries:
        for col, entry in enumerate(row):
            content = entry.get()
            if content:
                col_widths[col] = max(col_widths[col], len(content))
    
    for col, width in enumerate(col_widths):
        adjusted_width = min(width + 5, 50)
        scrollable_frame.grid_columnconfigure(col, minsize=adjusted_width * 8)
        
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.xview_moveto(0)

def reset_columns(original_column_widths, scrollable_frame, canvas):
    """Reset columns to their original widths"""
    for col, width in enumerate(original_column_widths):
        scrollable_frame.grid_columnconfigure(col, minsize=width * 10)
        
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.xview_moveto(0)
