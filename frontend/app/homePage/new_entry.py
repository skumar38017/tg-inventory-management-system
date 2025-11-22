# ~/frontend/app/homePage/new_entry.py

from turtle import width
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
    
    # Don't clear the added items list if it's from today
    global added_items_listbox
    today = datetime.now().date()
    if added_items_listbox:
        current_list_date = getattr(added_items_listbox, 'current_date', None)
        if current_list_date != today:
            # Clear all items from treeview
            for item in added_items_listbox.get_children():
                added_items_listbox.delete(item)
            added_items_listbox.current_date = today

def create_inventory_item(scrollable_frame, header_labels):
    """Add new inventory items from all rows with all fields optional"""
    from api_request.entry_inventory_api_request import add_new_inventory_item
    
    # Define required fields for validation
    required_fields = ['InventoryID', 'ProductID', 'Name', 'Material', 'TotalQuantity', 
                      'Manufacturer', 'PurchaseDealer', 'PurchaseAmount', 'RepairQuantity', 
                      'RepairCost', 'OnRent', 'VendorName', 'TotalRent', 
                      'RentedInventoryReturned', 'OnEvent', 'InOffice', 'InWarehouse', 
                      'IssuedQty', 'BalanceQty', 'PurchaseDate', 'PurchaseAmount', 'VendorName', 'TotalRent', 'Sno']
    
    added_items = []
    today = datetime.now().date()
    
    # Get all widgets in the scrollable frame
    widgets = scrollable_frame.grid_slaves()
    
    # Find the highest row number (excluding header row 0)
    max_row = 0
    for widget in widgets:
        row = widget.grid_info()['row']
        if row > max_row:
            max_row = row
    
    # Process each data row (starting from row 1)
    for row in range(1, max_row + 1):
        try:
            # Collect data from this row
            item_data = {}
            has_data = False
            
            for col, field in enumerate(header_labels):
                var_name = f"{field}_{row}" if row > 1 else field
                
                if var_name in entries:
                    widget = entries[var_name]
                    
                    if isinstance(widget, tk.Entry):
                        value = widget.get().strip()
                    elif hasattr(widget, 'get_date'):  # DateEntry
                        try:
                            date_value = widget.get_date()
                            value = date_value.strftime("%Y-%m-%d") if date_value else ""
                        except:
                            value = ""
                    elif isinstance(widget, tk.Checkbutton):
                        checkbox_var = checkbox_vars.get(var_name)
                        value = checkbox_var.get() if checkbox_var else False
                    else:
                        value = ""
                    
                    # Convert field name to API format
                    api_field = field.lower().replace(' ', '_')
                    item_data[api_field] = value
                    
                    # Check if this row has any data
                    if value and str(value).strip():
                        has_data = True
            
            # Only process rows that have some data
            if has_data:
                # Add current date to the item data
                item_data['added_date'] = today.strftime("%Y-%m-%d")
                added_item = add_new_inventory_item(item_data)
                added_items.append(added_item)
        except Exception as e:
            logger.error(f"Failed to add item (row {row}): {str(e)}")
            messagebox.showerror("Error", f"Failed to add item from row {row}\\nError: {str(e)}")
            continue
    
    # Check if no items were processed
    if not added_items:
        messagebox.showwarning("Warning", "No valid data found to add")
        return

    # Display results if any items were added
    if added_items:
        global added_items_listbox
        if added_items_listbox:
            # Only clear if we're starting a new day
            current_list_date = getattr(added_items_listbox, 'current_date', None)
            if current_list_date != today:
                # Clear all items from treeview
                for item in added_items_listbox.get_children():
                    added_items_listbox.delete(item)
                added_items_listbox.current_date = today
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for idx, item in enumerate(added_items, start=1):
                # Determine row tag for alternating colors
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                
                # Insert data into treeview
                added_items_listbox.insert('', 'end', values=(
                    f"{idx}. {item.get('id', 'N/A')}",
                    item.get('sno', 'N/A'),
                    item.get('inventory_id', 'N/A'),
                    item.get('product_id', 'N/A'),
                    item.get('name', 'N/A'),
                    item.get('material', 'N/A'),
                    item.get('total_quantity', 'N/A'),
                    item.get('manufacturer', 'N/A'),
                    item.get('purchase_dealer', 'N/A'),
                    item.get('purchase_date', 'N/A'),
                    item.get('purchase_amount', 'N/A'),
                    item.get('repair_quantity', 'N/A'),
                    item.get('repair_cost', 'N/A'),
                    item.get('submitted_by', 'N/A'),
                    item.get('inventory_barcode', 'N/A')
                ), tags=(tag,))
        
        # Refresh form and generate new IDs
        refresh_form(scrollable_frame, header_labels)
        messagebox.showinfo("Success", f"{len(added_items)} items added successfully")
    else:
        messagebox.showwarning("Warning", "No items were added")

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
    if field in ['On Rent', 'Rented Returned', 'On Event', 'In Office', 'In Warehouse']:
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
            width=universal_font_box_size.common * 2,
            justify='center'
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
    
    # Create canvas and scrollbars (using ttk.Scrollbar like Added Items List)
    canvas = tk.Canvas(scroll_container)
    h_scrollbar = ttk.Scrollbar(scroll_container, orient='horizontal', command=canvas.xview)
    v_scrollbar = ttk.Scrollbar(scroll_container, orient='vertical', command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
    
    # Apply the exact same scrollbar layout as Added Items List
    canvas.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')
    
    # Configure grid weights (same as Added Items List)
    scroll_container.grid_rowconfigure(0, weight=1)
    scroll_container.grid_columnconfigure(0, weight=1)
    
    # Apply modern scrolling (10x speed) - same as Added Items List
    setup_modern_scrolling(canvas, scrollable_frame)
    
    # Header row with field names
    header_labels = [
        'Sno', "InventoryID", "ProductID", 'Name', 'Material', 'Total Quantity', 
        'Manufacturer', 'Purchase Dealer', 'Purchase Date', 'Purchase Amount', 
        'Repair Quantity', 'Repair Cost', 'On Rent', 'Vendor Name', 'Total Rent', 
        'Rented Returned', 'Returned Date', 'On Event', 'In Office', 
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
    added_items_frame = tk.Frame(new_entry_frame, bg='white')
    added_items_frame.pack(fill='both', expand=True, padx=12, pady=(5, 12))
    
    # Added Items List header
    added_items_header = tk.Label(
        added_items_frame, 
        text="Added Items List (Today)", 
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.qr_barcode_header_font_size, 'bold'),
        bg='white', fg='#2c3e50', height=1
    )
    added_items_header.pack(anchor='w', pady=(0, 5))
    
    # Added Items List container with scrollbars
    added_list_container = tk.Frame(added_items_frame, bg='white', relief='sunken', bd=1)
    added_list_container.pack(fill='both', expand=True)
    
    # Create Treeview for table layout
    columns = ('ID', 'Serial No.', 'InventoryID', 'ProductID', 'Name', 'Material', 
               'Total Quantity', 'Manufacturer', 'Purchase Dealer', 'Purchase Date', 
               'Purchase Amount', 'Repair Quantity', 'Repair Cost', 'submitted_by', 'BarCode')
    
    global added_items_listbox
    added_items_listbox = ttk.Treeview(added_list_container, columns=columns, show='headings', height=8)
    
    # Configure column headings and widths
    added_items_listbox.heading('ID', text='[Today] ID')
    added_items_listbox.heading('Serial No.', text='Serial No.')
    added_items_listbox.heading('InventoryID', text='InventoryID')
    added_items_listbox.heading('ProductID', text='ProductID')
    added_items_listbox.heading('Name', text='Name')
    added_items_listbox.heading('Material', text='Material')
    added_items_listbox.heading('Total Quantity', text='Total Quantity')
    added_items_listbox.heading('Manufacturer', text='Manufacturer')
    added_items_listbox.heading('Purchase Dealer', text='Purchase Dealer')
    added_items_listbox.heading('Purchase Date', text='Purchase Date')
    added_items_listbox.heading('Purchase Amount', text='Purchase Amount')
    added_items_listbox.heading('Repair Quantity', text='Repair Quantity')
    added_items_listbox.heading('Repair Cost', text='Repair Cost')
    added_items_listbox.heading('submitted_by', text='submitted_by')
    added_items_listbox.heading('BarCode', text='BarCode')
    
    # Configure Treeview font styling with Excel-like appearance
    style = ttk.Style()
    style.configure('Treeview', font=(universal_font_box_size.qr_barcode_button_font_family, universal_font_box_size.new_entry_font_size))
    style.configure("Treeview", rowheight=35)  # Fixed row height for uniform rectangles
    
    # Excel-like grid appearance with uniform rectangular cells
    style.configure("Treeview", 
                   relief="solid", 
                   borderwidth=1,
                   fieldbackground="white")
    style.configure("Treeview.Heading", 
                   relief="solid", 
                   borderwidth=1,
                   background="#d4e6f1",
                   foreground="black",
                   anchor="center")  # Center align headers
    
    # Configure uniform column widths for equal rectangular cells
    uniform_width = 300  # Fixed width for all columns to create equal rectangles
    for col in columns:
        added_items_listbox.heading(col, text=col, anchor="center")
        added_items_listbox.column(col, width=uniform_width, minwidth=uniform_width, anchor='center', stretch=True)
    
    # Configure alternating row colors
    added_items_listbox.tag_configure('evenrow', background='#f5f5f5')  # Official gray
    added_items_listbox.tag_configure('oddrow', background='#ffffff')   # Pure white
    
    # Create scrollbars
    added_v_scrollbar = ttk.Scrollbar(added_list_container, orient='vertical', command=added_items_listbox.yview)
    added_h_scrollbar = ttk.Scrollbar(added_list_container, orient='horizontal', command=added_items_listbox.xview)
    added_items_listbox.configure(yscrollcommand=added_v_scrollbar.set, xscrollcommand=added_h_scrollbar.set)
    
    # Grid layout for proper scrollbar positioning
    added_items_listbox.grid(row=0, column=0, sticky='nsew')
    added_v_scrollbar.grid(row=0, column=1, sticky='ns')
    added_h_scrollbar.grid(row=1, column=0, sticky='ew')
    
    # Configure grid weights
    added_list_container.grid_rowconfigure(0, weight=1)
    added_list_container.grid_columnconfigure(0, weight=1)
    
    # Apply modern scrolling (10x speed)
    setup_modern_scrolling(added_items_listbox)
    style.configure('Treeview.Heading', font=(universal_font_box_size.qr_barcode_button_font_family, universal_font_box_size.new_entry_font_size, 'bold'))
 
    # Row styling
    added_items_listbox.tag_configure('evenrow', background='#f8f9fa')
    added_items_listbox.tag_configure('oddrow', background='#ffffff')
    
    # Set current date for the treeview
    today = datetime.now().date()
    added_items_listbox.current_date = today
    
    return new_entry_frame
