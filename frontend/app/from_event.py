# frontend/app/from_event.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from api_request.from_event_inventory_request import (
    create_to_return_inventory_list,
    load_submitted_project_return_from_db,
    update_submitted__return_project_in_db,
    search_return_details_by_id
)
from fromEvent.header import create_header_section, update_clock
from fromEvent.Information_fields import create_information_fields
from fromEvent.submitted_project import setup_submitted_tab
from fromEvent.search_result import setup_search_tab
from fromEvent.new_event_entry import generate_work_id, set_fields_readonly, clear_form, new_button_click
from fromEvent.edit_field import edit_record, update_record, validate_number, complete_refresh
import pandas as pd

class FromEventWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Tagglabs - Return From Event")

        # Configure global messagebox font for consistent appearance across all dialogs
        self.window.option_add('*Dialog.msg.font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))
        
        # Configure Combobox dropdown list font
        self.window.option_add('*TCombobox*Listbox.Font', (universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size))

        # Maximize window
        self.maximize_window()
        
        # Track wrap state
        self.is_wrapped = False
        self.original_column_widths = []

        # Get status options from StatusEnum
        self.status_options = [status.value for status in StatusEnum]
        
        # Database file
        self.db_file = "inventory_data.json"
        
        # Initialize database
        self.initialize_db()
        
        # Hide parent window (optional)
        self.parent.withdraw()
        
        # Setup the window
        self.setup_ui()
        
        # Handle window closing
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Focus on this window
        self.window.focus_set()
                
        # Set initial state
        self.set_fields_readonly(False)
        
        # Generate and set WorkID automatically
        self.generate_work_id()
        
        # Load initial data
        self.load_submitted_forms()
        
        logger.info("To Event window opened successfully")

    def initialize_db(self):
        """Initialize the JSON database file if it doesn't exist"""
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump([], f)
 
    def save_to_db(self, data, work_id=None):
        """Save data to the database via API"""
        try:
            work_id = data['work_id']

            # First check if project exists - handle 404 as non-error case
            try:
                existing_records = search_return_details_by_id(work_id)
                if existing_records:
                    # Update existing recordsave_to_db
                    if not update_submitted__return_project_in_db(work_id, data):
                        raise Exception("Failed to update record via API")
                    return True
            except Exception as e:
                logger.warning(f"Project check failed, attempting create: {str(e)}")

            # Create new record
            api_response = create_to_return_inventory_list(data)
            logger.info(f"New record created via API: {api_response}")
            return True

        except Exception as e:
            logger.error(f"Failed to save to database: {str(e)}")
            return False

    def load_from_db(self, work_id=None):
        """Load data from API only"""
        try:
            if work_id:
                # Load single record by work_id
                records = search_return_details_by_id(work_id)
                return records[0] if records else None
            else:
                # Load all records sorted by updated_at in descending order
                records = load_submitted_project_return_from_db()
                if records:
                    # Sort by updated_at in descending order
                    return sorted(records, key=lambda x: x.get('updated_at', ''), reverse=True)
                return []

        except Exception as e:
            logger.error(f"Failed to load from database: {str(e)}")
            return None

    def generate_work_id(self):
        """Generate a random WorkID"""
        return generate_work_id(self.work_id)

    def set_fields_readonly(self, readonly):
        """Set all fields to readonly or editable"""
        set_fields_readonly(self, readonly)

    def maximize_window(self):
        maximize_window(self.window)


    def setup_ui(self):
        """Set up all UI elements"""
        # Create header section
        self.clock_label_ref = {}
        create_header_section(self.window, self.clock_label_ref)
        update_clock(self.clock_label_ref, self.window)
        
        # Create information fields
        entries, self.fetch_btn, self.edit_btn, self.update_btn = create_information_fields(self.window, self)
        
        # Map entries to instance variables
        self.project_id = entries['project_id']
        self.employee_name = entries['employee_name']
        self.location = entries['location']
        self.client_name = entries['client_name']
        self.project_name = entries['project_name']
        self.setup_date = entries['setup_date']
        self.event_date = entries['event_date']
        self.work_id = entries['work_id']


        # Separator line
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # Inventory table
        self.table_frame = tk.Frame(self.window)
        self.table_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.table_frame)
        self.v_scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.pack(side="bottom", fill="x")

        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.yview_moveto(0)

        # Table headers
        self.headers = [
            "Zone/Activity", "Sr. No.", "Inventory", "Description",
            "Quantity", "Comments", "Total", "Units", "Per Unit Power (W)",
            "Total Power (W)", "Status", "POC", "RecQty"
        ]

        self.original_column_widths = [20 if col not in [4,6,7,8,9] else 15 for col in range(len(self.headers))]
        
        for col, header in enumerate(self.headers):
            tk.Label(self.scrollable_frame, text=header, 
                   font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'),
                   borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=col, sticky="ew")

        # Create entry fields
        self.table_entries = []
        for row in range(1, 2):  # 2 empty rows
            row_entries = []
            for col in range(len(self.headers)):
                if col == 10:  # Status column
                    # Create Combobox for Status
                    status_var = tk.StringVar()
                    combo = ttk.Combobox(
                        self.scrollable_frame,
                        textvariable=status_var,
                        values=self.status_options,
                        state="state",
                        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)
                    )
                    combo.set(self.status_options[0])  # Set default status
                    combo.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                    row_entries.append(combo)
                else:
                    # Regular Entry for other columns
                    entry = tk.Entry(self.scrollable_frame, 
                                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                                width=self.original_column_widths[col])
                    entry.grid(row=row, column=col, sticky="ew", padx=2, pady=2)
                    row_entries.append(entry)
            self.table_entries.append(row_entries)

        # Create Notebook for tabs
        self.tab_control = ttk.Notebook(self.window)
        self.tab_control.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5,0))

        # Tab 1: Submitted Projects
        self.submitted_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.submitted_tab, text="Submitted Projects")
        self.submitted_tree = setup_submitted_tab(self.submitted_tab, self)

        # Tab 2: Search Results
        self.search_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.search_tab, text="Search Results")
        self.search_tree = setup_search_tab(self.search_tab, self)

        # Bottom buttons
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.wrap_btn = tk.Button(button_frame, text="Wrap", command=self.toggle_wrap,
                                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
        self.wrap_btn.pack(side=tk.LEFT, padx=5)

        remove_row_btn = tk.Button(button_frame, text="Remove Row", command=self.remove_table_row,
                                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
        remove_row_btn.pack(side=tk.LEFT, padx=5)

        add_row_btn = tk.Button(button_frame, text="Add Row", command=self.add_table_row,
                              font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
        add_row_btn.pack(side=tk.LEFT, padx=5)

        submit_btn = tk.Button(button_frame, text="Submit", command=self.submit_form,
                             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
        submit_btn.pack(side=tk.LEFT, padx=5)

        return_button = tk.Button(button_frame, 
                                text="Return to Main", 
                                command=self.on_close,
                                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'),
                                width=15)
        return_button.pack(side=tk.RIGHT, padx=5)

        # Grid configuration
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

    def new_button_click(self):
        """Handle New Entry button click"""
        new_button_click(self)

    def load_submitted_forms(self):
        """Load all submitted forms into the submitted tab sorted by updated_at"""
        # Clear existing items
        for item in self.submitted_tree.get_children():
            self.submitted_tree.delete(item)
        
        records = self.load_from_db()
        
        if not records:
            return
        
        for record in records:
            # Format the updated_at timestamp for display
            updated_at = record.get('updated_at', '')
            if updated_at:
                try:
                    # Convert to datetime object and format
                    dt = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")
                except:
                    formatted_date = updated_at
            else:
                formatted_date = 'Not available'
            
            self.submitted_tree.insert("", "end", values=(
                record['work_id'],
                record['employee_name'],
                record['location'],
                record['project_name'],
                record['client_name'],
                record['setup_date'],
                record['event_date'],
                formatted_date  # Make sure this is included
            ))

    def fetch_record(self):
        """Search records by Work ID and display in Search Results tab"""
        work_id = self.project_id.get().strip()
        if not work_id:
            messagebox.showwarning("Warning", "Please enter a Work ID to search")
            return
            
        record = self.load_from_db(work_id)
        
        if not record:
            messagebox.showinfo("Info", f"No records found for Work ID: {work_id}")
            return
                
        # Clear existing items in search tab
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
            
        # Format the updated_at timestamp for display
        updated_at = record.get('updated_at', '')
        if updated_at:
            try:
                # Convert to datetime object and format
                dt = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")
            except:
                formatted_date = updated_at
        else:
            formatted_date = 'Not available'
            
        # Populate search tab with the found record
        self.search_tree.insert("", "end", values=(
            record['work_id'],
            record['project_name'],
            record['employee_name'],
            record['location'],
            record['client_name'],
            record['setup_date'],
            record['event_date'],
            formatted_date
        ))
        
        # Switch to search results tab
        self.tab_control.select(self.search_tab)

    def load_project_data(self, work_id):
        """Load project data into the form"""
        record = self.load_from_db(work_id)
        if not record:
            messagebox.showerror("Error", f"Record with Work ID {work_id} not found")
            return
        
        # Populate form fields
        self.work_id.config(state='normal')
        self.work_id.delete(0, tk.END)
        self.work_id.insert(0, record['work_id'])
        self.work_id.config(state='readonly')
        
        self.employee_name.delete(0, tk.END)
        self.employee_name.insert(0, record['employee_name'])
        
        self.location.delete(0, tk.END)
        self.location.insert(0, record['location'])
        
        self.client_name.delete(0, tk.END)
        self.client_name.insert(0, record['client_name'])
        
        # Fix for DateEntry widgets - use set_date() instead of insert()
        if record['setup_date']:
            try:
                # Parse the date string into datetime object
                if isinstance(record['setup_date'], str):
                    # Handle different date formats from API
                    try:
                        dt = datetime.strptime(record['setup_date'], '%Y-%m-%d')
                    except ValueError:
                        dt = datetime.strptime(record['setup_date'], '%Y-%m-%d')
                    self.setup_date.set_date(dt)
                else:
                    self.setup_date.set_date(record['setup_date'])
            except Exception as e:
                logger.error(f"Error setting setup date: {str(e)}")
                self.setup_date.set_date(datetime.now())
        
        self.project_name.delete(0, tk.END)
        self.project_name.insert(0, record['project_name'])
        
        # Fix for event_date DateEntry widget
        if record['event_date']:
            try:
                if isinstance(record['event_date'], str):
                    try:
                        dt = datetime.strptime(record['event_date'], '%Y-%m-%d')
                    except ValueError:
                        dt = datetime.strptime(record['event_date'], '%Y-%m-%d')
                    self.event_date.set_date(dt)
                else:
                    self.event_date.set_date(record['event_date'])
            except Exception as e:
                logger.error(f"Error setting event date: {str(e)}")
                self.event_date.set_date(datetime.now())
        
        # Clear existing table entries and add enough rows
        self.clear_table()
        
        # Add rows for all inventory items
        for _ in range(len(record.get('inventory_items', [])) - len(self.table_entries)):
            self.add_table_row()
        
        # Fill in the inventory items
        for i, item in enumerate(record.get('inventory_items', [])):
            if i >= len(self.table_entries):
                break
                    
            row = self.table_entries[i]
            # Ensure we have all the fields we need
            fields = [
                'zone_active', 'sno', 'name', 'description', 
                'quantity', 'comments', 'total', 'unit', 
                'per_unit_power', 'total_power', 'status', 'poc', 'RecQty'
            ]
            
            for col, field in enumerate(fields):
                if col < len(row):  # Make sure we don't exceed row length
                    if col == 10:  # Status column (Combobox)
                        row[col].set(item.get(field, self.status_options[0]))
                    else:  # Regular Entry
                        row[col].delete(0, tk.END)
                        value = str(item.get(field, ''))
                        row[col].insert(0, value)
        
        # Switch back to form view
        self.tab_control.select(0)
        
        # Set fields to readonly initially
        self.set_fields_readonly(True)
        self.edit_btn.config(state=tk.NORMAL)
        self.update_btn.config(state=tk.DISABLED)

    def clear_table(self):
        """Clear all table entries except the first row"""
        # Remove all rows except first one
        while len(self.table_entries) > 1:
            self.remove_table_row()
        
        # Clear the first row
        if self.table_entries:
            for entry in self.table_entries[0]:
                entry.delete(0, tk.END)

    def edit_record(self):
        """Enable editing of the record"""
        edit_record(self)

    def update_record(self):
        """Update the record in database"""
        update_record(self)

    def _validate_number(self, value, default=0):
        """Ensure numeric fields are valid"""
        return validate_number(value, default)

    def _complete_refresh(self, work_id):
        """Complete refresh after update"""
        complete_refresh(self, work_id)

    def _scroll_to_project(self, work_id):
        """Scroll to the updated project in the treeview"""
        for item in self.submitted_tree.get_children():
            if self.submitted_tree.item(item)['values'][0] == work_id:
                self.submitted_tree.selection_set(item)
                self.submitted_tree.see(item)
                break


    def refresh_after_update(self, work_id):
        """Refresh the form after successful update"""
        try:
            # Clear and reload the submitted forms list
            self.load_submitted_forms()
            
            # Reload the current project data
            self.load_project_data(work_id)
            
            # Switch to readonly mode
            self.set_fields_readonly(True)
            self.edit_btn.config(state=tk.NORMAL)
            self.update_btn.config(state=tk.DISABLED)
            
            # Ensure the updated project is visible in the list
            self.tab_control.select(self.submitted_tab)
            
            # Scroll to the updated project in the treeview
            for item in self.submitted_tree.get_children():
                if self.submitted_tree.item(item)['values'][0] == work_id:
                    self.submitted_tree.selection_set(item)
                    self.submitted_tree.see(item)
                    break
                    
        except Exception as e:
            logger.error(f"Refresh after update failed: {str(e)}", exc_info=True)

    def toggle_wrap(self):
        """Toggle between wrapped and original column sizes"""
        if not self.is_wrapped:
            self.adjust_columns()
            self.wrap_btn.config(text="Unwrap")
            self.is_wrapped = True
        else:
            self.reset_columns()
            self.wrap_btn.config(text="Wrap")
            self.is_wrapped = False

    def adjust_columns(self):
        """Adjust column widths based on content"""
        col_widths = [len(header) for header in self.headers]
        
        for row in self.table_entries:
            for col, entry in enumerate(row):
                content = entry.get()
                if content:
                    col_widths[col] = max(col_widths[col], len(content))
        
        for col, width in enumerate(col_widths):
            adjusted_width = min(width + 5, 50)
            self.scrollable_frame.grid_columnconfigure(col, minsize=adjusted_width * 8)
            
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.xview_moveto(0)

    def reset_columns(self):
        """Reset columns to their original widths"""
        for col, width in enumerate(self.original_column_widths):
            self.scrollable_frame.grid_columnconfigure(col, minsize=width * 10)
            
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.xview_moveto(0)

    def add_table_row(self):
        """Add a new row to the table"""
        current_rows = len(self.table_entries)
        
        row_entries = []
        for col in range(len(self.headers)):
            if col == 10:  # Status column
                status_var = tk.StringVar()
                combo = ttk.Combobox(
                    self.scrollable_frame,
                    textvariable=status_var,
                    values=self.status_options,
                    state="state",
                    font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)
                )
                combo.set(self.status_options[0])  # Set default status
                combo.grid(row=current_rows+1, column=col, sticky="ew", padx=2, pady=2)
                row_entries.append(combo)
            else:
                entry = tk.Entry(self.scrollable_frame, 
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                            width=self.original_column_widths[col])
                entry.grid(row=current_rows+1, column=col, sticky="ew", padx=2, pady=2)
                row_entries.append(entry)
        self.table_entries.append(row_entries)
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def remove_table_row(self):
        """Remove the last row from the table"""
        if len(self.table_entries) <= 1:
            messagebox.showwarning("Warning", "Cannot remove the last row")
            return
            
        last_row = self.table_entries.pop()
        for entry in last_row:
            entry.destroy()
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def submit_form(self):
        """Handle form submission with multiple inventory items"""
        try:
            # Get the current work_id
            work_id = self.work_id.get()
            if not work_id:
                messagebox.showwarning("Warning", "Work ID is required")
                return

            # Basic validation
            if not (self.employee_name.get() or self.client_name.get() or self.project_name.get()):
                messagebox.showwarning("Warning", "Please fill in at least one required field")
                return

            # Prepare data with all fields
            data = {
                'work_id': work_id,
                'employee_name': self.employee_name.get(),
                'location': self.location.get(),
                'client_name': self.client_name.get(),
                'setup_date': self.setup_date.get(),
                'project_name': self.project_name.get(),
                'event_date': self.event_date.get(),
                'submitted_by': "inventory-admin",  # Add this required field
                'inventory_items': []
            }

            # Add all inventory items with proper field mapping
            for row in self.table_entries:
                # Only add rows with at least name and quantity
                if row[2].get() and row[4].get():  # name and quantity fields
                    item = {
                        'work_id': work_id,
                        'zone_active': row[0].get() or "Default Zone",  # Provide default if empty
                        'sno': row[1].get() or "",  # Optional field
                        'name': row[2].get(),
                        'description': row[3].get() or "",  # Optional field
                        'quantity': int(row[4].get()) if row[4].get().isdigit() else 1,  # Convert to int
                        'comments': row[5].get() or "",  # Optional field
                        'total': row[6].get() if row[6].get().isdigit() else 0,  # Handle optional total field
                        'unit': row[7].get() or "pcs",  # Provide default if empty
                        'per_unit_power': float(row[8].get()) if row[8].get() and row[8].get().replace('.','',1).isdigit() else 0.0,
                        'total_power': float(row[9].get()) if row[9].get() and row[9].get().replace('.','',1).isdigit() else 0.0,
                        'status': row[10].get(),
                        'poc': row[11].get() or "",  # Optional field
                        'RecQty': row[12].get() if len(row) > 12 else ""  # Handle optional RecQty field
                    }
                    data['inventory_items'].append(item)

            if not data['inventory_items']:
                messagebox.showwarning("Warning", "At least one inventory item with name and quantity is required")
                return

            logger.debug(f"Sending payload: {data}")

            # Try to save to API
            if not self.save_to_db(data):
                raise Exception("Failed to save to database")

            messagebox.showinfo("Success", "Form submitted successfully")
            logger.info(f"Form submitted: {data}")

            # Clear form and generate new WorkID
            self.clear_form()
            self.generate_work_id()

            # Refresh submitted forms tab
            self.load_submitted_forms()
            self.tab_control.select(self.submitted_tab)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit form: {str(e)}")
            logger.error(f"Submit failed: {str(e)}")

    def clear_form(self):
        """Clear all form fields"""
        clear_form(self)
        self.set_fields_readonly(False)
        messagebox.showinfo("Cleared", "Form has been cleared")

    def refresh_data(self):
        """Refresh the form and data lists"""
        try:
            # Clear existing items
            self.clear_form()
            # If we have a work_id loaded, refresh that specific record
            current_work_id = self.work_id.get()              
            messagebox.showinfo("Refreshed", "Data has been refreshed")
            logger.info("Data refreshed successfully")
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh data: {str(e)}")
            logger.error(f"Refresh failed: {str(e)}")

    def on_close(self):
        """Handle window closing"""
        logger.info("Closing To Event window")
        self.window.destroy()
        self.parent.deiconify()