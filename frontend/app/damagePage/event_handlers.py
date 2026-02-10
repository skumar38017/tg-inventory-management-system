from common_imports import *

def bind_combobox_events(inventory_combobox, project_combobox, entries):
    """Bind events to comboboxes"""
    from damagePage.entry_wastage import on_inventory_selected, on_project_selected, update_project_combobox
    
    if inventory_combobox:
        inventory_combobox.bind("<<ComboboxSelected>>", 
            lambda e: on_inventory_selected(e, inventory_combobox, entries))
    
    if project_combobox:
        project_combobox.config(
            postcommand=lambda: update_project_combobox(inventory_combobox, project_combobox)
        )
        project_combobox.bind("<<ComboboxSelected>>", 
            lambda e: on_project_selected(e, inventory_combobox, project_combobox, entries))
