from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from api_request.damage_inventory_api_request import (
    submit_wastage_inventory,
    update_wastage_inventory,
    delete_wastage_inventory,
    show_all_wastage_inventory
)

def setup_wastage_entry_ui(parent, window, fields, display_names, status_options, entries, edit_mode_ref, current_edit_ref, refresh_callback):
    """Setup wastage entry UI section"""
    main_frame = tk.Frame(parent)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Input frame
    input_frame = tk.LabelFrame(main_frame, text="Enter Wastage Details", padx=5, pady=5,
                              font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    input_frame.pack(fill=tk.X, pady=5)
    
    # Scrollable container
    canvas = tk.Canvas(input_frame, height=300)
    h_scrollbar = tk.Scrollbar(input_frame, orient="horizontal", command=canvas.xview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(xscrollcommand=h_scrollbar.set)
    canvas.pack(side="top", fill="both", expand=True)
    h_scrollbar.pack(side="bottom", fill="x")
    
    # Create input fields
    for i, (field, display) in enumerate(zip(fields, display_names)):
        row = i % 5
        col = (i // 5) * 2
        
        tk.Label(scrollable_frame, text=display + ":",
                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=row, column=col, sticky=tk.E, padx=5, pady=2)
        
        if field == "inventory_name":
            combo_frame = tk.Frame(scrollable_frame)
            combo_frame.grid(row=row, column=col+1, sticky='ew', padx=5, pady=2)
            
            inventory_name_combobox = InventoryComboBox(
                combo_frame,
                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                width=universal_font_box_size.search_entry_width,
                height=15
            )
            window.option_add('*TCombobox*Listbox.Font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
            inventory_name_combobox.pack(fill=tk.X, expand=True, ipady=4)
            entries[field] = inventory_name_combobox
            
        elif field == "project_name":
            combo_frame = tk.Frame(scrollable_frame)
            combo_frame.grid(row=row, column=col+1, sticky='ew', padx=5, pady=2)
            
            project_name_combobox = ttk.Combobox(
                combo_frame,
                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                width=universal_font_box_size.search_entry_width,
                height=15
            )
            window.option_add('*TCombobox*Listbox.Font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
            project_name_combobox.pack(fill=tk.X, expand=True, ipady=4)
            entries[field] = project_name_combobox
            
        elif field in ["status", "wastage_status", "check_status"]:
            combo_frame = tk.Frame(scrollable_frame)
            combo_frame.grid(row=row, column=col+1, sticky='ew', padx=5, pady=2)
            
            combo = ttk.Combobox(combo_frame, values=status_options,
                               font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size),
                               width=universal_font_box_size.search_entry_width,
                               height=15, state="readonly")
            window.option_add('*TCombobox*Listbox.Font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
            combo.pack(fill=tk.X, expand=True, ipady=4)
            entries[field] = combo
            
        elif field in ["wastage_date", "event_date", "receive_date"]:
            date_frame = tk.Frame(scrollable_frame)
            date_frame.grid(row=row, column=col+1, sticky='ew', padx=5, pady=2)
            
            date_entry = DateEntry(date_frame, width=universal_font_box_size.search_entry_width-1, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                  font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
            date_entry.pack(fill=tk.X, expand=True, ipady=4)
            entries[field] = date_entry
            
        else:
            entry_frame = tk.Frame(scrollable_frame)
            entry_frame.grid(row=row, column=col+1, sticky='ew', padx=5, pady=2)
            
            entry = tk.Entry(entry_frame, width=universal_font_box_size.search_entry_width,
                           font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
            entry.pack(fill=tk.X, expand=True, ipady=4)
            entries[field] = entry
        
        if field == "wastage_date":
            entries[field].set_date(datetime.now().date())
        elif field == "status":
            entries[field].set("damaged")
    
    # Button frame
    button_frame = tk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)
    
    return main_frame, button_frame, entries

def new_entry(entries, edit_mode_ref, current_edit_ref):
    """Clear all fields for new entry"""
    if edit_mode_ref['mode']:
        if not messagebox.askyesno("Confirm", "Discard changes and create new entry?"):
            return
    
    for field, widget in entries.items():
        if isinstance(widget, ttk.Combobox):
            widget.set('')
            widget.config(state='normal')
        elif isinstance(widget, DateEntry):
            widget.set_date(datetime.now().date())
            widget.config(state='normal')
        else:
            widget.config(state='normal')
            widget.delete(0, tk.END)
    
    entries["wastage_date"].set_date(datetime.now().date())
    entries["status"].set("damaged")
    
    edit_mode_ref['mode'] = False
    current_edit_ref['id'] = None
    current_edit_ref['employee'] = None
    
    logger.info("Prepared form for new entry")

def submit_form(entries, edit_mode_ref, refresh_callback):
    """Submit new entry"""
    if edit_mode_ref['mode']:
        return update_selected(entries, edit_mode_ref, refresh_callback)
    
    data = {}
    for field, widget in entries.items():
        if isinstance(widget, ttk.Combobox):
            data[field] = widget.get().strip()
        elif isinstance(widget, DateEntry):
            data[field] = widget.get_date().strftime("%Y-%m-%d")
        else:
            data[field] = widget.get().strip()
    
    if not data["inventory_id"] or not data["employee_name"]:
        messagebox.showwarning("Warning", "Inventory ID and Employee Name are required")
        return
    
    success = submit_wastage_inventory({"wastages": [data]})
    
    if success:
        messagebox.showinfo("Success", "Entry submitted successfully")
        new_entry(entries, edit_mode_ref, {'id': None, 'employee': None})
        refresh_callback()
    else:
        messagebox.showerror("Error", "Failed to submit entry")

def update_selected(entries, edit_mode_ref, current_edit_ref, refresh_callback):
    """Update selected entry"""
    if not edit_mode_ref['mode'] or not current_edit_ref['id'] or not current_edit_ref['employee']:
        messagebox.showwarning("Warning", "No item selected for editing")
        return
    
    update_data = {
        "assign_to": entries["assign_to"].get().strip(),
        "sno": entries["sno"].get().strip(),
        "description": entries["description"].get().strip(),
        "quantity": entries["quantity"].get().strip(),
        "status": entries["status"].get().strip(),
        "receive_date": entries["receive_date"].get_date().strftime("%Y-%m-%d"),
        "receive_by": entries["receive_by"].get().strip(),
        "check_status": entries["check_status"].get().strip(),
        "location": entries["location"].get().strip(),
        "project_name": entries["project_name"].get().strip(),
        "comment": entries["comment"].get().strip(),
        "zone_activity": entries["zone_activity"].get().strip(),
        "wastage_reason": entries["wastage_reason"].get().strip(),
        "wastage_date": entries["wastage_date"].get_date().strftime("%Y-%m-%d"),
        "wastage_approved_by": entries["wastage_approved_by"].get().strip(),
        "wastage_status": entries["wastage_status"].get().strip()
    }
    
    success = update_wastage_inventory(
        employee_name=current_edit_ref['employee'],
        inventory_id=current_edit_ref['id'],
        data=update_data
    )
    
    if success:
        messagebox.showinfo("Success", "Entry updated successfully")
        new_entry(entries, edit_mode_ref, current_edit_ref)
        refresh_callback()
    else:
        messagebox.showerror("Error", "Failed to update entry")

def delete_selected(tree, fields, refresh_callback):
    """Delete selected entry"""
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "No item selected")
        return
        
    values = tree.item(selected, "values")
    if not values:
        return
        
    employee_name = values[fields.index("employee_name")]
    inventory_id = values[fields.index("inventory_id")]
    
    if not messagebox.askyesno("Confirm", f"Delete entry {inventory_id}?"):
        return
    
    success = delete_wastage_inventory(
        employee_name=employee_name,
        inventory_id=inventory_id
    )
    
    if success:
        messagebox.showinfo("Success", "Entry deleted successfully")
        refresh_callback()
    else:
        messagebox.showerror("Error", "Failed to delete entry")

def edit_selected(tree, fields, entries, edit_mode_ref, current_edit_ref):
    """Edit selected entry"""
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to edit")
        return
        
    values = tree.item(selected, "values")
    if not values:
        return
    
    for field, value in zip(fields, values):
        if isinstance(entries[field], ttk.Combobox):
            entries[field].set(value)
        elif isinstance(entries[field], DateEntry):
            try:
                date_val = datetime.strptime(value, "%Y-%m-%d").date()
                entries[field].set_date(date_val)
            except (ValueError, AttributeError):
                pass
        else:
            entries[field].delete(0, tk.END)
            entries[field].insert(0, value)
    
    for field in ["inventory_id", "employee_name", "product_id", "project_id"]:
        entries[field].config(state='readonly')
    
    edit_mode_ref['mode'] = True
    current_edit_ref['id'] = values[fields.index("inventory_id")]
    current_edit_ref['employee'] = values[fields.index("employee_name")]
    
    entries["assign_to"].focus_set()
    logger.info(f"Editing entry: {current_edit_ref['id']}")

def on_inventory_selected(event, inventory_combobox, entries):
    """Auto-fill fields when inventory selected"""
    selected_item = inventory_combobox.get_selected_item()
    if not selected_item:
        return
        
    fields_to_fill = {
        'product_id': selected_item.get('product_id', ''),
        'sno': selected_item.get('sno', ''),
        'inventory_id': selected_item.get('inventory_id', ''),
        'project_id': selected_item.get('project_id', ''),
        'description': selected_item.get('description', ''),
        'quantity': selected_item.get('quantity', ''),
        'location': selected_item.get('location', ''),
        'employee_name': selected_item.get('employee_name', ''),
        'assign_to': selected_item.get('assign_to', ''),
        'status': selected_item.get('status', ''),
        'zone_activity': selected_item.get('zone_activity', '')
    }
    
    for field, value in fields_to_fill.items():
        if field in entries:
            if isinstance(entries[field], ttk.Combobox):
                entries[field].set(value)
            elif isinstance(entries[field], DateEntry):
                try:
                    if value:
                        date_val = datetime.strptime(value, "%Y-%m-%d").date()
                        entries[field].set_date(date_val)
                except (ValueError, AttributeError):
                    pass
            else:
                entries[field].delete(0, tk.END)
                entries[field].insert(0, value)

def on_project_selected(event, inventory_combobox, project_combobox, entries):
    """Auto-fill fields when project selected"""
    selected_name = project_combobox.get()
    if not selected_name:
        return
        
    selected_inventory = inventory_combobox.get_selected_item()
    if not selected_inventory:
        return
        
    all_inventory = inventory_combobox.get_all_inventory_data()
    
    selected_project = None
    for item in all_inventory:
        if (item.get('project_name') == selected_name and 
            ((selected_inventory.get('product_id') and 
            item.get('product_id') == selected_inventory.get('product_id')) or
            (selected_inventory.get('inventory_id') and 
            item.get('inventory_id') == selected_inventory.get('inventory_id')))):
            selected_project = item
            break
    
    if selected_project:
        fields_to_fill = {
            'project_name': selected_project.get('project_name'),
            'project_id': selected_project.get('project_id', ''),
            'event_date': selected_project.get('event_date', ''),
            'location': selected_project.get('location', ''),
            'zone_activity': selected_project.get('zone_activity', '')
        }
        
        for field, value in fields_to_fill.items():
            if field in entries:
                if isinstance(entries[field], ttk.Combobox):
                    entries[field].set(value)
                elif isinstance(entries[field], DateEntry):
                    try:
                        if value:
                            date_val = datetime.strptime(value, "%Y-%m-%d").date()
                            entries[field].set_date(date_val)
                    except (ValueError, AttributeError):
                        pass
                else:
                    entries[field].delete(0, tk.END)
                    entries[field].insert(0, value)

def update_project_combobox(inventory_combobox, project_combobox):
    """Update project combobox with related projects"""
    try:
        selected_inventory = inventory_combobox.get_selected_item()
        
        if selected_inventory:
            all_inventory = inventory_combobox.get_all_inventory_data()
            
            related_projects = []
            for item in all_inventory:
                if (selected_inventory.get('product_id') and 
                    item.get('product_id') == selected_inventory.get('product_id')):
                    related_projects.append(item)
                elif (selected_inventory.get('inventory_id') and 
                    item.get('inventory_id') == selected_inventory.get('inventory_id')):
                    related_projects.append(item)
            
            project_names = list({item.get('project_name', '') 
                                for item in related_projects 
                                if item.get('project_name')})
            
            project_combobox['values'] = project_names
        else:
            project_data = show_all_wastage_inventory() or []
            project_names = list({item.get('project_name', '') 
                                for item in project_data 
                                if item.get('project_name')})
            project_combobox['values'] = project_names
            
    except Exception as e:
        logger.error(f"Error updating project combobox: {str(e)}")
        messagebox.showerror("Error", "Failed to load related projects")
