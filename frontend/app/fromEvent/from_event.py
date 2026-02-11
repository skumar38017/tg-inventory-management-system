# frontend/app/fromEvent/from_event.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from utils.window_utils import maximize_window
from fromEvent.header import create_header_section, update_clock
from fromEvent.Information_fields import create_information_fields
from fromEvent.submitted_project import setup_submitted_tab
from fromEvent.search_result import setup_search_tab
from fromEvent.new_event_entry import generate_work_id, set_fields_readonly
from fromEvent.edit_field import edit_record, update_record
from fromEvent.database_operations import initialize_db
from fromEvent.table_operations import (
    create_inventory_table, add_table_row, remove_table_row, 
    clear_table, toggle_wrap
)
from fromEvent.bottom_buttons import create_bottom_buttons
from fromEvent.form_submission import submit_form
from fromEvent.data_loading import load_submitted_forms, fetch_record, load_project_data

class FromEventWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs - Return From Event")

        self.window.option_add('*Dialog.msg.font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
        self.window.option_add('*TCombobox*Listbox.Font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))

        maximize_window(self.window)
        
        self.is_wrapped = False
        self.original_column_widths = []
        self.status_options = [status.value for status in StatusEnum]
        self.db_file = "inventory_data.json"
        
        initialize_db(self.db_file)
        self.parent.withdraw()
        self.setup_ui()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.focus_set()
                
        set_fields_readonly(self, False)
        generate_work_id(self.work_id)
        self.load_submitted_forms()
        
        logger.info("From Event window opened successfully")

    def setup_ui(self):
        """Set up all UI elements"""
        self.clock_label_ref = {}
        create_header_section(self.window, self.clock_label_ref, "Return From Event Inventory List")
        update_clock(self.clock_label_ref, self.window)
        
        entries, self.fetch_btn, self.edit_btn, self.update_btn = create_information_fields(self.window, self)
        
        self.project_id = entries['project_id']
        self.employee_name = entries['employee_name']
        self.location = entries['location']
        self.client_name = entries['client_name']
        self.project_name = entries['project_name']
        self.setup_date = entries['setup_date']
        self.event_date = entries['event_date']
        self.work_id = entries['work_id']

        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        (self.table_frame, self.canvas, self.scrollable_frame, 
         self.headers, self.original_column_widths, self.table_entries) = create_inventory_table(
            self.window, self.status_options
        )

        self.tab_control = ttk.Notebook(self.window)
        self.tab_control.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5,0))

        self.submitted_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.submitted_tab, text="Submitted Projects")
        self.submitted_tree = setup_submitted_tab(self.submitted_tab, self)

        self.search_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.search_tab, text="Search Results")
        self.search_tree = setup_search_tab(self.search_tab, self)

        callbacks = {
            'toggle_wrap': self.toggle_wrap_handler,
            'remove_row': self.remove_table_row_handler,
            'add_row': self.add_table_row_handler,
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

    def toggle_wrap_handler(self):
        """Toggle between wrapped and original column sizes"""
        self.is_wrapped = toggle_wrap(
            self.is_wrapped, self.headers, self.table_entries, 
            self.scrollable_frame, self.canvas, self.original_column_widths
        )
        self.wrap_btn.config(text="Unwrap" if self.is_wrapped else "Wrap")

    def add_table_row_handler(self):
        """Add a new row to the table"""
        add_table_row(self.scrollable_frame, self.table_entries, self.headers, 
                     self.original_column_widths, self.status_options, self.canvas)

    def remove_table_row_handler(self):
        """Remove the last row from the table"""
        remove_table_row(self.table_entries, self.canvas)

    def submit_form(self):
        """Handle form submission"""
        submit_form(self)

    def load_submitted_forms(self):
        """Load all submitted forms"""
        load_submitted_forms(self)

    def fetch_record(self):
        """Search records by Work ID"""
        fetch_record(self)

    def load_project_data(self, work_id):
        """Load project data into the form"""
        load_project_data(self, work_id)

    def edit_record(self):
        """Enable editing of the record"""
        edit_record(self)

    def update_record(self):
        """Update the record in database"""
        update_record(self)

    def new_button_click(self):
        """Handle New Entry button click"""
        from fromEvent.new_event_entry import new_button_click
        new_button_click(self)

    def clear_form(self):
        """Clear all form fields"""
        from fromEvent.new_event_entry import clear_form
        clear_form(self)

    def refresh_data(self):
        """Refresh the form and data lists"""
        try:
            self.clear_form()
            current_work_id = self.work_id.get()
            messagebox.showinfo("Refreshed", "Data has been refreshed")
            logger.info("Data refreshed successfully")
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh data: {str(e)}")
            logger.error(f"Refresh failed: {str(e)}")

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing From Event window")
        self.window.destroy()
        self.parent.deiconify()
