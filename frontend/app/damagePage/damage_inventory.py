# frontend/app/damagePage/damage_inventory.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from utils.window_utils import maximize_window
from damagePage.entry_wastage import setup_wastage_entry_ui, new_entry, submit_form, delete_selected
from damagePage.update_inventory import edit_selected, update_selected
from damagePage.search_inventory import setup_search_ui, search_inventory
from damagePage.result import setup_results_ui, display_results
from damagePage.action_buttons import create_action_buttons
from damagePage.data_operations import refresh_data, on_tree_select
from damagePage.event_handlers import bind_combobox_events

class DamageWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Inventory Damage/Waste Management")
        
        self.window.option_add('*Dialog.msg.font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
        
        maximize_window(self.window)
        self.status_options = [status.value for status in StatusEnum]
        
        self.fields = [
            "assign_to", "sno", "employee_name", "inventory_id", "project_id",
            "product_id", "inventory_name", "description", "quantity", "status",
            "receive_date", "receive_by", "check_status", "location", "project_name",
            "event_date", "comment", "zone_activity", "wastage_reason", "wastage_date",
            "wastage_approved_by", "wastage_status"
        ]
        
        self.display_names = [
            "Assign To", "S.No", "Employee Name", "Inventory ID", "Project ID",
            "Product ID", "Inventory Name", "Description", "Quantity", "Status",
            "Receive Date", "Receive By", "Check Status", "Location", "Project Name",
            "Event Date", "Comment", "Zone/Activity", "Wastage Reason", "Wastage Date",
            "Approved By", "Wastage Status"
        ]
        
        self.edit_mode_ref = {'mode': False}
        self.current_edit_ref = {'id': None, 'employee': None}
        self.entries = {}
        
        self.parent.withdraw()
        self.setup_ui()
        self.refresh_data()
        self.window.focus_set()
        
        logger.info("Damage/Waste Management window opened successfully")

    def setup_ui(self):
        """Set up all UI elements"""
        main_container = tk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        main_frame, button_frame, self.entries = setup_wastage_entry_ui(
            main_container, self.window, self.fields, self.display_names, 
            self.status_options, self.entries, self.edit_mode_ref, self.current_edit_ref, 
            self.refresh_data
        )
        
        self.inventory_name_combobox = self.entries.get('inventory_name')
        self.project_name_combobox = self.entries.get('project_name')
        
        bind_combobox_events(self.inventory_name_combobox, self.project_name_combobox, self.entries)
        
        callbacks = {
            'new': self.new_entry,
            'submit': self.submit_form,
            'edit': self.edit_selected,
            'update': self.update_selected,
            'delete': self.delete_selected,
            'refresh': self.refresh_data,
            'close': self.on_close
        }
        create_action_buttons(button_frame, callbacks)
        
        search_frame, self.search_entries = setup_search_ui(main_container, self.search_inventory)
        results_frame, self.tree = setup_results_ui(main_container, self.display_names, self.on_tree_select_handler)

    def new_entry(self):
        new_entry(self.entries, self.edit_mode_ref, self.current_edit_ref)

    def submit_form(self):
        submit_form(self.entries, self.edit_mode_ref, self.refresh_data)

    def update_selected(self):
        update_selected(self.entries, self.edit_mode_ref, self.current_edit_ref, self.refresh_data)

    def delete_selected(self):
        delete_selected(self.tree, self.fields, self.refresh_data)

    def edit_selected(self):
        edit_selected(self.tree, self.fields, self.entries, self.edit_mode_ref, self.current_edit_ref)

    def search_inventory(self):
        results = search_inventory(self.search_entries)
        display_results(self.tree, results, self.fields)

    def on_tree_select_handler(self, event):
        self.selected_item, values = on_tree_select(self.tree, self.fields, event)

    def refresh_data(self):
        refresh_data(self.tree, self.fields)

    def on_close(self):
        logger.info("Closing Damage Inventory window")
        self.window.destroy()
        self.parent.deiconify()
