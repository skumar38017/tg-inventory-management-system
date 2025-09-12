# ~/frontend/app/homePage/new_entry.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

# Global variables
entries = {}
checkbox_vars = {}
added_items_listbox = None

def clear_fields():
    """Clear all input fields except InventoryID and ProductID, and reset checkboxes"""
    # Create a copy of entries to avoid modification during iteration
    entries_copy = dict(entries)
    
    for field_name, entry in entries_copy.items():
        # Skip InventoryID and ProductID fields (including numbered ones like InventoryID_2)
        if 'InventoryID' not in field_name and 'ProductID' not in field_name:
            try:
                if hasattr(entry, 'delete'):
                    entry.delete(0, tk.END)
                elif hasattr(entry, 'set'):
                    entry.set(False)
            except tk.TclError:
                # Widget has been destroyed, remove from entries dict
                if field_name in entries:
                    del entries[field_name]

def refresh_form(scrollable_frame, header_labels):
    """Refresh the form by clearing fields and regenerating IDs for all rows"""
    clear_fields()
    
    # Create a copy of entries to avoid modification during iteration
    entries_copy = dict(entries)
    
    # Regenerate IDs for all InventoryID and ProductID fields
    for field_name, entry in entries_copy.items():
        try:
            if 'InventoryID' in field_name:
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, generate_inventory_id())
                entry.config(state='readonly')
            elif 'ProductID' in field_name:
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, generate_product_id())
                entry.config(state='readonly')
        except tk.TclError:
            # Widget has been destroyed, remove from entries dict
            if field_name in entries:
                del entries[field_name]

def create_inventory_item(scrollable_frame, header_labels):
    """Add new inventory items from all rows with all fields optional"""
    pass  # Placeholder - implement as needed

def remove_last_row(scrollable_frame):
    """Remove the last row from the form"""
    # Get all widgets in the scrollable frame
    widgets = scrollable_frame.grid_slaves()
    
    # Find the highest row number (excluding header row 0)
    max_row = 0
    for widget in widgets:
        row = widget.grid_info()['row']
        if row > max_row:
            max_row = row
    
    # Don't remove if only header and one data row exist
    if max_row <= 1:
        messagebox.showwarning("Warning", "Cannot remove the last remaining row!")
        return
    
    # Remove all widgets from the last row and clean up entries
    widgets_to_remove = []
    for widget in widgets:
        if widget.grid_info()['row'] == max_row:
            widgets_to_remove.append(widget)
    
    # Remove widgets and clean up entries dictionary
    for widget in widgets_to_remove:
        widget.destroy()
    
    # Clean up entries dictionary - remove entries for the deleted row
    entries_to_remove = []
    for field_name in entries.keys():
        if field_name.endswith(f'_{max_row}'):
            entries_to_remove.append(field_name)
    
    for field_name in entries_to_remove:
        del entries[field_name]
        if field_name in checkbox_vars:
            del checkbox_vars[field_name]

def create_single_date_entry(parent_frame, row, col):
    """Create a single date entry with standardized styling"""
    date_frame = tk.Frame(parent_frame)
    date_frame.grid(row=row, column=col, sticky="ew", padx=1, pady=1)
    
    # Create DateEntry with same styling as date range picker
    date_entry = DateEntry(
        date_frame,
        width=22,
        background='#3498db',
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd',
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.date_box_size),
        calendar_font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.date_box_size),
        calendar_width=universal_font_box_size.ID * 10,
        calendar_height=universal_font_box_size.ID * 10
    )
    date_entry.delete(0, 'end')
    date_entry.pack(side='left', fill=tk.X, expand=True)
    
    # Add clear button
    clear_btn = tk.Button(
        date_frame,
        text="X",
        command=lambda e=date_entry: e.delete(0, 'end'),
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.date_box_size),
        width=3,
        relief='flat',
    )
    clear_btn.pack(side='right', padx=(2,0))
    
    return date_entry

def create_field_for_row(scrollable_frame, field, col, row, var_name):
    """Create a single field for a specific row - reusable function"""
    if field in ['On Rent', 'Rented Inventory Returned', 'On Event', 'In Office', 'In Warehouse']:
        checkbox_vars[var_name] = tk.BooleanVar()
        entries[var_name] = tk.Checkbutton(
            scrollable_frame, 
            variable=checkbox_vars[var_name],
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.new_entry_font_size),
            width=universal_font_box_size.common * 2,
            height=1
        )
        entries[var_name].grid(row=row, column=col, sticky='ew', padx=1, pady=1)
    elif field in ['Purchase Date', 'Returned Date']:
        entries[var_name] = create_single_date_entry(scrollable_frame, row, col)
    else:
        entries[var_name] = tk.Entry(
            scrollable_frame, 
            font=('Helvetica', universal_font_box_size.new_entry_font_size), 
            borderwidth=1,
            relief='solid',
            width=int(universal_font_box_size.common * 2)
        )
        entries[var_name].grid(row=row, column=col, sticky='ew', padx=1, pady=1)
        
        if field == 'InventoryID':
            entries[var_name].insert(0, generate_inventory_id())
            entries[var_name].config(state='readonly')
        elif field == 'ProductID':
            entries[var_name].insert(0, generate_product_id())
            entries[var_name].config(state='readonly')

def add_new_row(scrollable_frame, header_labels):
    """Add a new row to the form"""
    widgets = scrollable_frame.grid_slaves()
    max_row = max([widget.grid_info()['row'] for widget in widgets])
    new_row = max_row + 1
    
    for col, field in enumerate(header_labels):
        var_name = f"{field.replace(' ', '')}_{new_row}"
        create_field_for_row(scrollable_frame, field, col, new_row, var_name)

def create_new_entry_tab(notebook):
    """Create the New Entry tab with all its components"""
    # Frame 2: New Entry
    new_entry_frame = tk.Frame(notebook, bg='white')
    notebook.add(new_entry_frame, text="New Entry")
    
    # Main container for the form
    form_container = tk.Frame(new_entry_frame)
    form_container.pack(fill='both', expand=True, padx=12, pady=5)
    
    # Container for the header and input rows with scrollbars
    scroll_container = tk.Frame(form_container)
    scroll_container.pack(fill='both', expand=True)
    
    # Create canvas and scrollbars
    canvas = tk.Canvas(scroll_container)
    h_scrollbar = tk.Scrollbar(scroll_container, orient='horizontal', command=canvas.xview)
    v_scrollbar = tk.Scrollbar(scroll_container, orient='vertical', command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
    
    # Setup modern scrolling features
    setup_modern_scrolling(canvas, scrollable_frame)
    
    # Grid layout for canvas and scrollbars
    canvas.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')
    
    # Configure grid weights
    scroll_container.grid_rowconfigure(0, weight=1)
    scroll_container.grid_columnconfigure(0, weight=1)
    
    # Header row with field names
    header_labels = [
        'Sno', "InventoryID", "ProductID", 'Name', 'Material', 'Total Quantity', 
        'Manufacturer', 'Purchase Dealer', 'Purchase Date', 'Purchase Amount', 
        'Repair Quantity', 'Repair Cost', 'On Rent', 'Vendor Name', 'Total Rent', 
        'Rented Inventory Returned', 'Returned Date', 'On Event', 'In Office', 
        'In Warehouse', 'Issued Qty', 'Balance Qty', 'Submited by'
    ]
    
    # Create header row
    for col, label in enumerate(header_labels):
        header = tk.Label(scrollable_frame, text=label, 
                         font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.new_entry_font_size, 'bold'), borderwidth=1, relief='solid',
                         height=1, width=int(universal_font_box_size.common * 2), anchor='center')
        header.grid(row=0, column=col, sticky='ew', padx=1, pady=1)
    
    # Create first row of input fields using reusable function
    for col, field in enumerate(header_labels):
        var_name = field.replace(' ', '')
        create_field_for_row(scrollable_frame, field, col, 1, var_name)
                        
    # Configure column weights
    for col in range(len(header_labels)):
        scrollable_frame.grid_columnconfigure(col, weight=1)

    # Button container
    button_frame = tk.Frame(form_container)
    button_frame.pack(fill='x', pady=2)
    
    # Left side buttons (Clear and Refresh)
    clear_button = tk.Button(
        button_frame, 
        text="Clear", 
        command=clear_fields,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size),
        width=universal_font_box_size.button_width
    )
    clear_button.pack(side='left', padx=2)

    refresh_button = tk.Button(
        button_frame, 
        text="Refresh", 
        command=lambda: refresh_form(scrollable_frame, header_labels),
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size),
        width=universal_font_box_size.button_width
    )
    refresh_button.pack(side='left', padx=2)

    # Center button (Add Item) with expand
    add_button = tk.Button(
        button_frame, 
        text="Add Item", 
        command=lambda: create_inventory_item(scrollable_frame, header_labels),
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold'),
        width=universal_font_box_size.button_width
    )
    add_button.pack(side='left', padx=5, expand=True)

    # Right side buttons (Remove Row and Add Row)
    remove_row_button = tk.Button(
        button_frame, 
        text="Remove Row", 
        command=lambda: remove_last_row(scrollable_frame),
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size,),
        width=universal_font_box_size.button_width
    )
    remove_row_button.pack(side='left', padx=5)

    add_row_button = tk.Button(
        button_frame, 
        text="Add Row", 
        command=lambda: add_new_row(scrollable_frame, header_labels),
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size),
        width=universal_font_box_size.button_width
    )
    add_row_button.pack(side='left', padx=2)
        
    # Added Items List section
    list_frame = tk.Frame(new_entry_frame)
    list_frame.pack(fill='both', expand=True, padx=12, pady=5)
    
    # "Added Items List" label centered
    list_label = tk.Label(
        list_frame, 
        text="Added Items List", 
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_button_font_size, 'bold')
    )
    list_label.pack()
    
    # Create container for the listbox with both scrollbars
    list_container = tk.Frame(list_frame)
    list_container.pack(fill='both', expand=True)

    # Create horizontal scrollbar first (placed at bottom)
    h_scrollbar = tk.Scrollbar(
        list_container,
        orient="horizontal",
        command=lambda *args: added_items_listbox.xview(*args)
    )
    h_scrollbar.pack(side="bottom", fill="x")
    
    added_items_listbox = tk.Listbox(
        list_container,
        height=12,
        font=('Courier New', universal_font_box_size.search_button_font_size),
        selectbackground='#4a6984',
        selectforeground='white',
        xscrollcommand=h_scrollbar.set,
        yscrollcommand=v_scrollbar.set
    )
    added_items_listbox.pack(side="left", fill="both", expand=True)

    # Add vertical scrollbar
    list_scrollbar = tk.Scrollbar(
        list_container,
        orient="vertical",
        command=added_items_listbox.yview
    )
    list_scrollbar.pack(side="right", fill="y")
    added_items_listbox.config(yscrollcommand=list_scrollbar.set)

    # Setup modern scrolling for Added Items List
    setup_modern_scrolling(added_items_listbox)

    return new_entry_frame
