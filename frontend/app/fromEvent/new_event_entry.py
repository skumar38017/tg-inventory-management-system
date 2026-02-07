from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
import random
import string

def generate_work_id(work_id_entry):
    """Generate a random WorkID in format PRJ followed by 5 digits"""
    prefix = "PRJ"
    digits = ''.join(random.choices(string.digits, k=5))
    work_id = f"{prefix}{digits}"
    work_id_entry.config(state='normal')
    work_id_entry.delete(0, tk.END)
    work_id_entry.insert(0, work_id)
    work_id_entry.config(state='readonly')
    return work_id

def set_fields_readonly(parent_instance, readonly):
    """Set all fields to readonly or editable"""
    state = 'readonly' if readonly else 'normal'
    
    # Main fields
    parent_instance.employee_name.config(state=state)
    parent_instance.location.config(state=state)
    parent_instance.client_name.config(state=state)
    parent_instance.setup_date.config(state=state)
    parent_instance.project_name.config(state=state)
    parent_instance.event_date.config(state=state)
    parent_instance.work_id.config(state='readonly')  # Always readonly
    parent_instance.project_id.config(state='normal')  # Project ID is editable for fetching
    
    # Table entries
    for row in parent_instance.table_entries:
        for entry in row:
            entry.config(state=state)

def clear_form(parent_instance):
    """Clear all form fields and generate new Work ID"""
    try:
        parent_instance.project_id.delete(0, tk.END)
        parent_instance.employee_name.delete(0, tk.END)
        parent_instance.location.delete(0, tk.END)
        parent_instance.client_name.delete(0, tk.END)
        
        # Clear DateEntry widgets properly
        parent_instance.setup_date.set_date(datetime.now().strftime('%Y-%m-%d'))
        parent_instance.project_name.delete(0, tk.END)
        parent_instance.event_date.set_date(datetime.now().strftime('%Y-%m-%d'))
        
        # Clear table entries
        for row in parent_instance.table_entries:
            for entry in row:
                entry.delete(0, tk.END)
        
        # Generate new Work ID
        generate_work_id(parent_instance.work_id)
        
        logger.info("Form cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing form: {e}")
        messagebox.showerror("Error", f"Failed to clear form: {str(e)}")

def new_button_click(parent_instance):
    """Handle New Entry button click - clears the form and generates new Work ID"""
    clear_form(parent_instance)
    generate_work_id(parent_instance.work_id)
    set_fields_readonly(parent_instance, False)
    messagebox.showinfo("New Entry", "Ready to create a new entry")
