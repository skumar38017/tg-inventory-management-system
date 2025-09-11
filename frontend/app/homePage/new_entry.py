# ~/frontend/app/homePage/new_entry.py

from common_imports import *

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
    
    # Grid layout for canvas and scrollbars
    canvas.grid(row=0, column=0, sticky='nsew')
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    h_scrollbar.grid(row=1, column=0, sticky='ew')
    
    # Configure grid weights
    scroll_container.grid_rowconfigure(0, weight=1)
    scroll_container.grid_columnconfigure(0, weight=1)
    
    # Create the entry form inside the scrollable frame
    global entries, checkbox_vars
    entries = {}
    checkbox_vars = {}
    
    # Header row with field names
    header_labels = [
        'Sno', "InventoryID", "ProductID", 'Name', 'Material', 'Total Quantity', 
        'Manufacturer', 'Purchase Dealer', 'Purchase Date', 'Purchase Amount', 
        'Repair Quantity', 'Repair Cost', 'On Rent', 'Vendor Name', 'Total Rent', 
        'Rented Inventory Returned', 'Returned Date', 'On Event', 'In Office', 
        'In Warehouse', 'Issued Qty', 'Balance Qty', 'Submited by'
    ]
    
    # Create header row (i)
    for col, label in enumerate(header_labels):
        header = tk.Label(scrollable_frame, text=label, 
                         font=('Helvetica', 9, 'bold'), borderwidth=1, relief='solid')
        header.grid(row=0, column=col, sticky='ew', padx=1, pady=1)
    
    # In the create_list_frames function, where you create the first row of input fields:
    for col, field in enumerate(header_labels):
        var_name = field.replace(' ', '')
        if field in ['On Rent', 'Rented Inventory Returned', 'On Event', 'In Office', 'In Warehouse']:
            checkbox_vars[var_name] = tk.BooleanVar()
            entries[var_name] = tk.Checkbutton(
                scrollable_frame, 
                variable=checkbox_vars[var_name],
                borderwidth=1,
                relief='solid'
            )
            entries[var_name].grid(row=1, column=col, sticky='ew', padx=1, pady=1)
        elif field in ['Purchase Date', 'Returned Date']:
            # Create a frame to hold the date entry and clear button
            date_frame = tk.Frame(scrollable_frame)
            date_frame.grid(row=1, column=col, sticky="ew", padx=1, pady=1)
            
            # Create DateEntry widget without setting a default date
            date_entry = DateEntry(
                date_frame,
                width=12,  # Slightly reduced to accommodate clear button
                background='darkblue',
                foreground='white',
                borderwidth=1,
                date_pattern='yyyy-mm-dd',
                font=('Helvetica', 9))
            date_entry.delete(0, 'end')  # Clear any default date
            date_entry.pack(side='left', fill=tk.X, expand=True)
            
            # Add clear button
            clear_btn = tk.Button(
                date_frame,
                text="✕",
                command=lambda e=date_entry: e.delete(0, 'end'),
                font=('Helvetica', 7),
                width=1,
                relief='flat',
            )
            clear_btn.pack(side='right', padx=(2,0))
            
            entries[var_name] = date_entry
        else:
            entries[var_name] = tk.Entry(
                scrollable_frame, 
                font=('Helvetica', 9), 
                borderwidth=1,
                relief='solid'
            )
            entries[var_name].grid(row=1, column=col, sticky='ew', padx=1, pady=1)
            
            # Auto-fill InventoryID and ProductID for the first row
            if field == 'InventoryID':
                entries[var_name].insert(0, generate_inventory_id())
                entries[var_name].config(state='readonly')
            elif field == 'ProductID':
                entries[var_name].insert(0, generate_product_id())
                entries[var_name].config(state='readonly')
                        
            # Configure column weights
            for col in range(len(header_labels)):
                scrollable_frame.grid_columnconfigure(col, weight=1)

    # Button container
    button_frame = tk.Frame(form_container)
    button_frame.pack(fill='x', pady=5)
    
    # Left side buttons (Clear and Refresh)
    clear_button = tk.Button(
        button_frame, 
        text="Clear", 
        command=clear_fields,
        font=('Helvetica', 12),
        width=25
    )
    clear_button.pack(side='left', padx=2)

    refresh_button = tk.Button(
        button_frame, 
        text="Refresh", 
        command=lambda: refresh_form(scrollable_frame, header_labels),
        font=('Helvetica', 12),
        width=25
    )
    refresh_button.pack(side='left', padx=2)

    # Center button (Add Item) with expand
    add_button = tk.Button(
        button_frame, 
        text="Add Item", 
        command=lambda: create_inventory_item(scrollable_frame, header_labels),
        font=('Helvetica', 12, 'bold'),
        width=25
    )
    add_button.pack(side='left', padx=5, expand=True)

    # Right side buttons (Remove Row and Add Row)
    remove_row_button = tk.Button(
        button_frame, 
        text="Remove Row", 
        command=lambda: remove_last_row(scrollable_frame),
        font=('Helvetica', 12, 'bold'),
        width=25
    )
    remove_row_button.pack(side='left', padx=5)

    add_row_button = tk.Button(
        button_frame, 
        text="Add Row", 
        command=lambda: add_new_row(scrollable_frame, header_labels),
        font=('Helvetica', 12, 'bold'),
        width=25
    )
    add_row_button.pack(side='left', padx=2)
        
    # Added Items List section
    list_frame = tk.Frame(new_entry_frame)
    list_frame.pack(fill='both', expand=True, padx=12, pady=5)
    
    # "Added Items List" label centered
    list_label = tk.Label(
        list_frame, 
        text="Added Items List", 
        font=('Helvetica', 12, 'bold')
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
    
    global added_items_listbox
    added_items_listbox = tk.Listbox(
        list_container,
        height=12,
        font=('Courier New', 11),  # Changed to fixed-width font for better alignment
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

    return new_entry_frame
