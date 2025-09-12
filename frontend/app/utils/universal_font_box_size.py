# ~/app/utils/universal_font_box_size.py

# Universal font size and box size for all the widgets

class UniversalFontBoxSize:
    # New entry tab specific (24pt fonts)
    new_entry_font_size = 24
    new_entry_input_width = 20
    new_entry_header_width = 20
    new_entry_header_height = 1

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
    
    
universal_font_box_size = UniversalFontBoxSize()
