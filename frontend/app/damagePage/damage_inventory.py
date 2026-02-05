# frontend/app/damage_inventory.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from api_request.damage_inventory_api_request import (
    search_wastage_inventory_by_id,
    show_all_wastage_inventory
)
from damagePage.wastage_inventory import (
    setup_wastage_entry_ui,
    new_entry,
    submit_form,
    update_selected,
    delete_selected,
    edit_selected,
    on_inventory_selected,
    on_project_selected,
    update_project_combobox
)
from damagePage.search_inventory import setup_search_ui, search_inventory

class DamageWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Inventory Damage/Waste Management")
        
        self.window.option_add('*Dialog.msg.font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
        
        self.maximize_window()
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

    def maximize_window(self):
        maximize_window(self.window)

    def setup_ui(self):
        """Set up all UI elements"""
        main_container = tk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Setup wastage entry section
        main_frame, button_frame, self.entries = setup_wastage_entry_ui(
            main_container, self.window, self.fields, self.display_names, 
            self.status_options, self.entries, self.edit_mode_ref, self.current_edit_ref, 
            self.refresh_data
        )
        
        # Get references to comboboxes
        self.inventory_name_combobox = self.entries.get('inventory_name')
        self.project_name_combobox = self.entries.get('project_name')
        
        # Bind events
        if self.inventory_name_combobox:
            self.inventory_name_combobox.bind("<<ComboboxSelected>>", 
                lambda e: on_inventory_selected(e, self.inventory_name_combobox, self.entries))
        
        if self.project_name_combobox:
            self.project_name_combobox.config(
                postcommand=lambda: update_project_combobox(self.inventory_name_combobox, self.project_name_combobox)
            )
            self.project_name_combobox.bind("<<ComboboxSelected>>", 
                lambda e: on_project_selected(e, self.inventory_name_combobox, self.project_name_combobox, self.entries))
        
        # Action buttons
        tk.Button(button_frame, text="New", command=self.new_entry,
                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Submit", command=self.submit_form,
                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit", command=self.edit_selected,
                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update", command=self.update_selected,
                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", command=self.delete_selected,
                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.refresh_data,
                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).pack(side=tk.LEFT, padx=5)
        
        # Setup search section
        search_frame, self.search_entries = setup_search_ui(main_container, self.search_inventory)
        
        # Results frame
        results_frame = tk.LabelFrame(main_container, text="Results", padx=5, pady=5,
                                    font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(results_frame, columns=self.display_names, show="headings")
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        for col, name in enumerate(self.display_names):
            self.tree.heading(col, text=name)
            self.tree.column(col, width=400, minwidth=250)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        tk.Button(button_frame, text="Return to Main", command=self.on_close,
                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

    def new_entry(self):
        """Clear all fields for a new entry"""
        new_entry(self.entries, self.edit_mode_ref, self.current_edit_ref)

    def submit_form(self):
        """Submit new entry"""
        submit_form(self.entries, self.edit_mode_ref, self.refresh_data)

    def update_selected(self):
        """Update selected entry"""
        update_selected(self.entries, self.edit_mode_ref, self.current_edit_ref, self.refresh_data)

    def delete_selected(self):
        """Delete selected entry"""
        delete_selected(self.tree, self.fields, self.refresh_data)

    def edit_selected(self):
        """Edit selected entry"""
        edit_selected(self.tree, self.fields, self.entries, self.edit_mode_ref, self.current_edit_ref)

    def search_inventory(self):
        """Search inventory"""
        results = search_inventory(self.search_entries)
        self.display_results(results)

    def on_tree_select(self, event):
        """Handle selection from treeview"""
        selected = self.tree.focus()
        if selected:
            self.selected_item = selected
            values = self.tree.item(selected, "values")
            if values:
                logger.info(f"Item selected: {values[self.fields.index('inventory_id')]}")

    def refresh_data(self):
        """Refresh all data from API"""
        results = show_all_wastage_inventory()
        self.display_results(results)
        logger.info("Data refreshed")

    def display_results(self, results):
        """Display results in treeview"""
        self.tree.delete(*self.tree.get_children())
        if results:
            for item in results:
                values = [item.get(field, "") for field in self.fields]
                self.tree.insert("", tk.END, values=values)

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing Damage Inventory window")
        self.window.destroy()
        self.parent.deiconify()