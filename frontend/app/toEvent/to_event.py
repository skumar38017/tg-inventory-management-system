# frontend/app/to_event.py

from common_imports import *
from api_request.to_event_inventory_request import (
    create_to_event_inventory_list, 
    load_submitted_project_from_db,
    update_submitted_project_in_db,
    search_project_details_by_id
)
from toEvent.bottom_buttons import create_bottom_buttons
from toEvent.header import create_header_section, update_clock
from toEvent.Information_fields import create_information_fields
from toEvent.database_operations import initialize_db, save_to_db, load_from_db
from toEvent.inventory_table import create_inventory_table, add_table_row, remove_table_row, clear_table, toggle_wrap
from toEvent.submitted_project import setup_submitted_tab, load_submitted_forms
from toEvent.search_result import setup_search_tab, fetch_record
from toEvent.data_loading import load_project_data
from toEvent.edit_field import edit_record, update_record
from toEvent.form_submission import submit_form
from toEvent.new_event_entry import new_button_click, generate_work_id, set_fields_readonly, clear_form

class ToEventWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs - To Event")

        self.window.option_add('*Dialog.msg.font', ('Arial', 12))
        maximize_window(self.window)

        self.is_wrapped = False
        self.original_column_widths = []
        self.status_options = [status.value for status in StatusEnum]
        self.db_file = "inventory_data.json"
        self.inventory_combo_data = []
        self.clock_label_ref = {}
        
        initialize_db(self.db_file)
        self.parent.withdraw()
        self.setup_ui()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.focus_set()
        set_fields_readonly(self, False)
        generate_work_id(self.work_id)
        self.load_submitted_forms()
        
        logger.info("To Event window opened successfully")

    def setup_ui(self):
        """Set up all UI elements"""
        create_header_section(self.window, self.clock_label_ref, "To Create Event Inventory List")
        update_clock(self.clock_label_ref, self.window)

        entries, self.fetch_btn, self.edit_btn, self.update_btn = create_information_fields(self.window, self)
        self.project_id = entries['project_id']
        self.employee_name = entries['employee_name']
        self.location = entries['location']
        self.client_name = entries['client_name']
        self.setup_date = entries['setup_date']
        self.project_name = entries['project_name']
        self.event_date = entries['event_date']
        self.work_id = entries['work_id']

        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        self.canvas, self.scrollable_frame, self.headers, self.original_column_widths = create_inventory_table(self.window, self)
        self.table_entries = []
        self.table_frame = self.canvas.master

        self.tab_control = ttk.Notebook(self.window)
        self.tab_control.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5,0))

        self.submitted_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.submitted_tab, text="Submitted Projects")
        self.submitted_tree = setup_submitted_tab(self.submitted_tab, self)

        self.search_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.search_tab, text="Search Results")
        self.search_tree = setup_search_tab(self.search_tab, self)

        callbacks = {
            'toggle_wrap': self.toggle_wrap,
            'remove_row': self.remove_table_row,
            'add_row': self.add_table_row,
            'submit': self.submit_form,
            'close': self.on_close
        }
        self.wrap_btn = create_bottom_buttons(self.window, callbacks)

        self.window.grid_rowconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=0)
        self.window.grid_rowconfigure(2, weight=0)
        self.window.grid_rowconfigure(3, weight=0)
        self.window.grid_rowconfigure(4, weight=0)
        self.window.grid_rowconfigure(5, weight=1)
        self.window.grid_rowconfigure(6, weight=1)
        self.window.grid_rowconfigure(7, weight=0)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        self.add_table_row()

    def save_to_db(self, data, work_id=None):
        return save_to_db(data)

    def load_from_db(self, work_id=None):
        return load_from_db(work_id)

    def generate_work_id(self):
        return generate_work_id(self.work_id)

    def set_fields_readonly(self, readonly):
        set_fields_readonly(self, readonly)

    def new_button_click(self):
        new_button_click(self)

    def load_submitted_forms(self):
        load_submitted_forms(self.submitted_tree)

    def load_submitted_project(self, event):
        selected = self.submitted_tree.selection()
        if selected:
            item = self.submitted_tree.item(selected)
            work_id = item['values'][0]
            self.load_project_data(work_id)

    def fetch_record(self):
        fetch_record(self)

    def load_search_result(self, event):
        selected = self.search_tree.selection()
        if selected:
            item = self.search_tree.item(selected)
            work_id = item['values'][0]
            self.load_project_data(work_id)

    def load_project_data(self, work_id):
        load_project_data(self, work_id)

    def clear_table(self):
        clear_table(self.table_entries)

    def edit_record(self):
        edit_record(self)

    def update_record(self):
        update_record(self)

    def toggle_wrap(self):
        self.is_wrapped = toggle_wrap(self.is_wrapped, self.wrap_btn, self.headers, 
                                      self.scrollable_frame, self.table_entries, self.canvas)

    def add_table_row(self):
        add_table_row(self.scrollable_frame, self.table_entries, self.headers, 
                     self.original_column_widths, self.status_options, self.canvas)

    def remove_table_row(self):
        remove_table_row(self.table_entries, self.canvas)

    def submit_form(self):
        submit_form(self)

    def clear_form(self):
        clear_form(self)

    def refresh_data(self):
        from toEvent.new_event_entry import clear_form
        clear_form(self)
        messagebox.showinfo("Refreshed", "Data has been refreshed")

    def on_close(self):
        logger.info("Closing To Event window")
        self.window.destroy()
        self.parent.deiconify()
