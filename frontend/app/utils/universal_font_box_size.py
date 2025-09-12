# ~/app/utils/universal_font_box_size.py

# Universal font size and box size for all the widgets

class UniversalFontBoxSize:
    # New entry tab specific 
    new_entry_font_size = 24
    new_entry_input_width = 20
    new_entry_header_width = 20
    new_entry_header_height = 1

    # Search fields specific
    search_label_font_size = 18
    search_label_font_family = 'Helvetica'
    search_label_font_weight = 'bold'
    search_entry_font_size = 18
    search_entry_font_family = 'Helvetica'
    search_entry_width = 20
    search_entry_relief = 'flat'
    search_entry_bd = 5

    # Search buttons specific
    search_button_font_size = 18
    search_button_font_family = 'Helvetica'
    search_button_font_weight = 'bold'
    search_button_height = 1
    search_button_width = 12
    search_button_relief = 'flat'

    # QR & Barcode button specific
    qr_barcode_button_width = 15
    qr_barcode_button_height = 1

    # Search frame spacing and sizing
    search_frame_bg = 'white'
    search_fields_frame_bg = '#ecf0f1'
    search_fields_frame_relief = 'raised'
    search_fields_frame_bd = 1
    search_frame_pady = 8
    search_frame_padx = 8
    search_grid_padx = 5
    search_grid_pady = 8
    search_separator_pady = 5
    search_label_fg = '#2c3e50'

    # Search results listbox height calculation
    search_screen_height_offset = 180
    search_height_multiplier = 0.8
    search_min_listbox_height = 8
    search_height_divisor = 35

    # Search results header definitions
    # Define inventory item headers for project search
    inventory_item_headers = [
        ("S.No", 30),
        ("Name", 50),
        ("Description", 50),
        ("Qty", 16),
        ("Zone", 35),
        ("Material", 40),
        ("Comments", 50),
        ("Total", 16),
        ("Unit", 16),
        ("Per Unit Power", 25),
        ("Total Power", 25),
        ("Status", 25),
        ("POC", 40),
        ("Item ID", 40)
    ]

    # Define the column headers and their display widths for inventory search
    inventory_column_headers = [
        ("ID", 50),
        ("Serial No.", 30),
        ("InventoryID", 20),
        ("Product ID", 20),
        ("Name", 50),
        ("Material", 40),
        ("Total Quantity", 25),
        ("Manufacturer", 40),
        ("Purchase Dealer", 40),
        ("Purchase Date", 35),
        ("Purchase Amount", 25),
        ("Repair Quantity", 25),
        ("Repair Cost", 25),
        ("On Rent", 30),
        ("Vendor Name", 40),
        ("Total Rent", 25),
        ("Rented Inventory Returned", 30),
        ("Returned Date", 30),
        ("On Event", 25),
        ("In Office", 30),
        ("In Warehouse", 35),
        ("Issued Qty", 25),
        ("Balance Qty", 25),
        ("Submitted By", 35),
        ("Created At", 40),
        ("Updated At", 40),
        ("BarCode", 40),
        ("BacodeUrl", 150)
    ]

    # Search results separator constants
    search_separator_length = 125

    # Legacy sizes (keep for backward compatibility)
    regular_font_size = 24
    regular_box_size = 24
    regular_drop_down_box_size = 24

    date_box_size = 22
    button_font_size = 18
    button_box_size = 20
    header_button_font_size = 14
    header_button_box_size = 10

    label_font_size = 18
    label_box_size = 18

    Bottom_button_font_size = 18
    Bottom_button_box_size = 20
    button_width = 10
    button_height = 1
    
    calendar_font_size = 28
    calendar_box_size = 28
    calendar_width = 2600
    calendar_height = 2600
    
    # Standardized sizes from entry_update_pop_window.py, entry_inventory.py, new_entry.py
    
    # Standard Input Fields (Entry, ComboBox, DateEntry)
    drop_down_box_size = 22
    drop_down_font_size = 22

    input_font_size = 20
    input_width = 22
    input_height = 2
    
    # Standard Labels
    label_font_size_standard = 18
    label_width = 18
    label_font_weight = 'bold'
    
    # Standard Buttons
    button_font_size_standard = 18
    button_width_small = 8      # Edit button
    button_width_medium = 10    # Update button
    button_width_large = 12     # Load Record, bottom buttons
    button_height_standard = 1
    
    # New Entry Tab specific (24pt fonts)
    new_entry_font_size = 24
    new_entry_input_width = 22
    new_entry_header_width = 20
    new_entry_header_height = 1
    
    # Checkbox specific
    checkbox_font_size = 20
    checkbox_width = 20
    checkbox_height = 2
    
    # Date Entry specific
    date_entry_font_size = 20
    date_entry_width = 22
    date_clear_button_width = 3
    date_clear_button_font = 18
    
    # Main inventory list
    inventory_list_font_size = 12
    inventory_list_font_family = 'Consolas'
    
    # Search results
    search_results_font_size = 11
    search_results_font_family = 'Courier New'
    
    # Added items list
    added_items_font_size = 24
    added_items_font_family = 'Courier New'
    added_items_height = 12
    
    
    #  All fields 
    ID=50
    S_No=30
    InventoryID=20
    Product_ID=20
    Name=50
    Material=40
    Total_Quantity=25
    Manufacturer=40
    Purchase_Dealer=40
    Purchase_Date=35
    Purchase_Amount=25
    Repair_Quantity=25
    Repair_Cost=25
    On_Rent=30
    Vendor_Name=40
    Total_Rent=25
    Rented_Inventory_Returned=30
    Returned_Date=30
    On_Event=25
    In_Office=30
    In_Warehouse=35
    Issued_Qty=25
    Balance_Qty=25
    Submitted_By=35
    Created_At=40
    Updated_At=40
    BarCode=40
    BarcodeUrl=150
    Description=50
    Qty=16
    Zone=35
    Material=40
    Comments=50
    Total=16
    Unit=16
    Per_Unit_Power=25
    Total_Power=25
    Status=25
    POC=40
    Item_ID=40


universal_font_box_size = UniversalFontBoxSize()
