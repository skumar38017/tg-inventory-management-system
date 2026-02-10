from common_imports import *

def submit_form(self):
    """Handle form submission with multiple inventory items"""
    try:
        work_id = self.work_id.get()
        if not work_id:
            messagebox.showwarning("Warning", "Work ID is required")
            return

        if not (self.employee_name.get() or self.client_name.get() or self.project_name.get()):
            messagebox.showwarning("Warning", "Please fill in at least one required field")
            return

        data = {
            'work_id': work_id,
            'employee_name': self.employee_name.get(),
            'location': self.location.get(),
            'client_name': self.client_name.get(),
            'setup_date': self.setup_date.get(),
            'project_name': self.project_name.get(),
            'event_date': self.event_date.get(),
            'submitted_by': "inventory-admin",
            'inventory_items': []
        }

        for row in self.table_entries:
            if row[2].get() and row[4].get():
                item = {
                    'work_id': work_id,
                    'zone_active': row[0].get() or "Default Zone",
                    'sno': row[1].get() or "",
                    'name': row[2].get(),
                    'description': row[3].get() or "",
                    'quantity': int(row[4].get()) if row[4].get().isdigit() else 1,
                    'comments': row[5].get() or "",
                    'total': row[6].get() if row[6].get().isdigit() else 0,
                    'unit': row[7].get() or "pcs",
                    'per_unit_power': float(row[8].get()) if row[8].get() and row[8].get().replace('.','',1).isdigit() else 0.0,
                    'total_power': float(row[9].get()) if row[9].get() and row[9].get().replace('.','',1).isdigit() else 0.0,
                    'status': row[10].get(),
                    'poc': row[11].get() or "",
                    'RecQty': row[12].get() if len(row) > 12 else ""
                }
                data['inventory_items'].append(item)

        if not data['inventory_items']:
            messagebox.showwarning("Warning", "At least one inventory item with name and quantity is required")
            return

        logger.debug(f"Sending payload: {data}")

        from fromEvent.database_operations import save_to_db
        if not save_to_db(data):
            raise Exception("Failed to save to database")

        messagebox.showinfo("Success", "Form submitted successfully")
        logger.info(f"Form submitted: {data}")

        from fromEvent.new_event_entry import clear_form, generate_work_id
        clear_form(self)
        generate_work_id(self.work_id)

        self.load_submitted_forms()
        self.tab_control.select(self.submitted_tab)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to submit form: {str(e)}")
        logger.error(f"Submit failed: {str(e)}")
