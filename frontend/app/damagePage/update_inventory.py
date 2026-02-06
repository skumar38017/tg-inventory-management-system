from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from api_request.damage_inventory_api_request import update_wastage_inventory

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
        # Clear edit mode
        edit_mode_ref['mode'] = False
        current_edit_ref['id'] = None
        current_edit_ref['employee'] = None
        refresh_callback()
    else:
        messagebox.showerror("Error", "Failed to update entry")
