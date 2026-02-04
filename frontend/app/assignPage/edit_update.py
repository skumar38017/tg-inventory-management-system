# frontend/app/assignPage/edit_update.py

from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from api_request.assign_inventory_api_request import (
    update_assigned_inventory,
    delete_assigned_inventory
)

class EditUpdateSection:
    def __init__(self, parent_window, parent_instance):
        self.window = parent_window
        self.parent = parent_instance
        
    # ---------------------------------------- Edit/Update section --------------------------------------------
    def edit_selected_entry(self):
        """Enable editing of the selected entry in new entry tree"""
        selected_item = self.parent.new_entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to edit")
            return
        
        # Get all column values
        item = selected_item[0]
        values = self.parent.new_entry_tree.item(item, 'values')
        
        # Create a top-level edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Record")
        
        # List of read-only fields (these won't be editable)
        read_only_fields = ['ID', 'Inventory ID', 'Inventory Name','Project ID', 'Product ID', 'Assigned Date', 'Assignment Return Date', 'Assignment Barcode', 'Employee Name', 'Assigned By']
        
        # Date fields that should use DateEntry widgets
        date_fields = [ 'Submission Date']
        
        # Create entry fields for each column
        entry_widgets = []
        for i, (header, value) in enumerate(zip(self.parent.headers, values)):
            tk.Label(edit_window, text=header).grid(row=i, column=0, padx=5, pady=2)
            
            if header in read_only_fields:
                # Create a label for read-only fields
                label = tk.Label(edit_window, text=value, relief="sunken", bg="#f0f0f0")
                label.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
                entry_widgets.append(label)  # Still append to maintain order
            elif header in date_fields:
                # Create a frame to hold the date entry
                date_frame = tk.Frame(edit_window)
                date_frame.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                
                # Create DateEntry widget
                date_entry = DateEntry(
                    date_frame,
                    width=18,
                    background='darkblue',
                    foreground='white',
                    borderwidth=2,
                    date_pattern='yyyy-mm-dd'
                )
                
                # Set the date if available
                try:
                    if value and value.strip():
                        date_entry.set_date(datetime.strptime(value, '%Y-%m-%d'))
                except ValueError:
                    pass
                
                date_entry.pack(fill=tk.X, expand=True)
                entry_widgets.append(date_entry)
            elif header == "Status":
                # Create a Combobox for Status field
                status_frame = tk.Frame(edit_window)
                status_frame.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                
                status_var = tk.StringVar()
                status_combo = ttk.Combobox(
                    status_frame,
                    textvariable=status_var,
                    values=self.parent.status_options,
                    state="readonly"
                )
                status_combo.set(value if value else "Assigned")
                status_combo.pack(fill=tk.X, expand=True)
                entry_widgets.append(status_combo)
            else:
                # Create an entry widget for editable fields
                entry = tk.Entry(edit_window)
                entry.insert(0, value)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
                entry_widgets.append(entry)
        
        # Save button
        save_btn = tk.Button(edit_window, text="Save Changes",
                            command=lambda: self.save_edited_entry(entry_widgets, edit_window))
        save_btn.grid(row=len(self.parent.headers), column=0, columnspan=2, pady=5)
        
        # Make the window resizable
        edit_window.grid_columnconfigure(1, weight=1)

    def save_edited_entry(self, entry_widgets, edit_window):
        """Save the edited entry back to the new entry tree"""
        try:
            # Get all edited values
            edited_values = []
            for i, widget in enumerate(entry_widgets):
                if isinstance(widget, tk.Label):  # Read-only field
                    edited_values.append(widget.cget("text"))
                elif isinstance(widget, DateEntry):  # DateEntry field
                    edited_values.append(widget.get_date().strftime('%Y-%m-%d'))
                elif isinstance(widget, ttk.Combobox):  # Combobox field (Status)
                    edited_values.append(widget.get())
                else:  # Regular Entry field
                    edited_values.append(widget.get())
            
            # Update the record in new entry tree
            selected_item = self.parent.new_entry_tree.selection()
            if selected_item:
                self.parent.new_entry_tree.item(selected_item[0], values=edited_values)
            
            # Close the edit window
            edit_window.destroy()
            
        except Exception as e:
            logger.error(f"Error saving edited entry: {e}")
            messagebox.showerror("Error", "Failed to save edited entry")
            
    def update_selected_entry(self):
        """Update the selected entry in the database using employee_name and inventory_id"""
        selected_item = self.parent.new_entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to update")
            return
        
        try:
            # Get the updated values
            item = selected_item[0]
            values = self.parent.new_entry_tree.item(item, 'values')
            
            # Ensure we have enough values
            if len(values) < 14:
                messagebox.showerror("Error", "Incomplete record data")
                return
                
            # Get the required identifiers from the treeview
            employee_name = values[3]  # Employee Name is at index 3
            inventory_id = values[4]   # Inventory ID is at index 4
            
            if not employee_name or not inventory_id:
                messagebox.showerror("Error", "Employee Name and Inventory ID are required for update")
                return
                
            # Prepare the update data according to API spec
            update_data = {
                'assign_to': values[2] or "",  # Assigned To
                'sno': values[1] or "",  # SNo
                'zone_activity': "",  # zone_activity
                'description': values[8] or "",  # Description
                'quantity': values[9] or "1",  # Quantity
                'status': values[10].lower() if values[10].lower() in ["assigned", "returned"] else "assigned",  # Status
                'purpose_reason': values[13] or "",  # Purpose/Reason
                'comment': values[15] or "",  # Comments
                'submission_date': self.parent.format_api_date(values[12]) or datetime.now().isoformat(),
                'assigned_date': self.parent.format_api_date(values[11]) or datetime.now().strftime('%Y-%m-%d'),
                'assignment_return_date': self.parent.format_api_date(values[16]) or (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'),
                'employee_name': employee_name,
                'inventory_id': inventory_id
            }
            
            # Call the API to update
            success = update_assigned_inventory(employee_name, inventory_id, update_data)
            if success:
                messagebox.showinfo("Success", "Record updated successfully")
                self.parent.refresh_assigned_inventory_list()
                self.parent.load_recent_submissions()
                self.parent.clear_form()
            else:
                messagebox.showerror("Error", "Failed to update record. Check logs for details.")
                
        except Exception as e:
            logger.error(f"Error updating record: {e}")
            messagebox.showerror("Error", f"Failed to update record: {str(e)}")

    def delete_selected_entry(self):
        """Delete the selected entry from the database"""
        selected_item = self.parent.new_entry_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return
        
        if not self.parent.currently_editing_id:
            messagebox.showwarning("Warning", "No record selected for deletion")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            try:
                # Call the API to delete
                success = delete_assigned_inventory(self.parent.currently_editing_id)
                if success:
                    messagebox.showinfo("Success", "Record deleted successfully")
                    self.parent.new_entry_tree.delete(selected_item)
                    self.parent.refresh_assigned_inventory_list()
                    self.parent.load_recent_submissions()
                    self.parent.clear_form()
                else:
                    messagebox.showerror("Error", "Failed to delete record")
                    
            except Exception as e:
                logger.error(f"Error deleting record: {e}")
                messagebox.showerror("Error", f"Failed to delete record: {str(e)}")

    # ---------------------------------------- End of Edit/Update section --------------------------------------------
