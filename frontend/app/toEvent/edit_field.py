from common_imports import *
from toEvent.database_operations import save_to_db

def edit_record(parent_instance):
    """Enable editing of the record"""
    if not parent_instance.work_id.get():
        messagebox.showwarning("Warning", "No record loaded to edit")
        return
        
    parent_instance.set_fields_readonly(False)
    parent_instance.edit_btn.config(state=tk.DISABLED)
    parent_instance.update_btn.config(state=tk.NORMAL)
    logger.info("Editing record")

def update_record(parent_instance):
    """Update the record in database via API with multiple rows"""
    try:
        work_id = parent_instance.work_id.get()
        if not work_id:
            messagebox.showwarning("Warning", "Work ID is required for update")
            return
            
        data = {
            'work_id': work_id,
            'employee_name': parent_instance.employee_name.get() or '',
            'location': parent_instance.location.get() or '',
            'client_name': parent_instance.client_name.get() or '',
            'setup_date': parent_instance.setup_date.get() or '',
            'project_name': parent_instance.project_name.get() or '',
            'event_date': parent_instance.event_date.get() or '',
            'inventory_items': []
        }
        
        for row_idx, row in enumerate(parent_instance.table_entries, start=1):
            if not row[2].get().strip():
                continue
                
            try:
                item = {
                    'zone_active': row[0].get() or 'General',
                    'sno': row[1].get() or str(row_idx),
                    'name': row[2].get(),
                    'description': row[3].get() or '',
                    'quantity': validate_number(row[4].get(), default=1),
                    'comments': row[5].get() or '',
                    'total': validate_number(row[6].get(), default=0),
                    'unit': row[7].get() or 'pcs',
                    'per_unit_power': validate_number(row[8].get(), default=0),
                    'total_power': validate_number(row[9].get(), default=0),
                    'status': row[10].get(),
                    'poc': row[11].get() or '',
                    'RecQty': row[12].get() if len(row) > 12 else ''
                }
                data['inventory_items'].append(item)
            except Exception as e:
                logger.error(f"Error processing row {row_idx}: {str(e)}")
                continue
                    
        if not data['inventory_items']:
            messagebox.showwarning("Warning", "No valid inventory items to update")
            return
            
        logger.debug(f"Prepared update data for {work_id} with {len(data['inventory_items'])} items")
        
        if not save_to_db(data):
            raise Exception("Failed to persist changes to database")
            
        complete_refresh(parent_instance, work_id)
        
        messagebox.showinfo("Success", f"Updated {len(data['inventory_items'])} items successfully")
        
    except Exception as e:
        messagebox.showerror("Error", f"Update failed: {str(e)}")
        logger.error(f"Update error: {str(e)}", exc_info=True)

def validate_number(value, default=0):
    """Ensure numeric fields are valid"""
    try:
        if not value:
            return default
        return float(value) if '.' in value else int(value)
    except:
        return default

def complete_refresh(parent_instance, work_id):
    """Complete refresh after update"""
    try:
        from toEvent.submitted_project import load_submitted_forms
        load_submitted_forms(parent_instance.submitted_tree)
        
        parent_instance.load_project_data(work_id)
        
        parent_instance.set_fields_readonly(True)
        parent_instance.edit_btn.config(state=tk.NORMAL)
        parent_instance.update_btn.config(state=tk.DISABLED)
        
        parent_instance.tab_control.select(parent_instance.submitted_tab)
        scroll_to_project(parent_instance, work_id)
        
    except Exception as e:
        logger.error(f"Refresh error: {str(e)}", exc_info=True)

def scroll_to_project(parent_instance, work_id):
    """Scroll to the updated project in the treeview"""
    for item in parent_instance.submitted_tree.get_children():
        if parent_instance.submitted_tree.item(item)['values'][0] == work_id:
            parent_instance.submitted_tree.selection_set(item)
            parent_instance.submitted_tree.see(item)
            break
