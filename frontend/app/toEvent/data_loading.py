from common_imports import *

def load_submitted_forms(self):
    """Load all submitted forms into the submitted tab sorted by updated_at"""
    for item in self.submitted_tree.get_children():
        self.submitted_tree.delete(item)
    
    from fromEvent.database_operations import load_from_db
    records = load_from_db()
    
    if not records:
        return
    
    for record in records:
        updated_at = record.get('updated_at', '')
        if updated_at:
            try:
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
            formatted_date
        ))

def fetch_record(self):
    """Search records by Work ID and display in Search Results tab"""
    work_id = self.project_id.get().strip()
    if not work_id:
        messagebox.showwarning("Warning", "Please enter a Work ID to search")
        return
    
    from fromEvent.database_operations import load_from_db
    record = load_from_db(work_id)
    
    if not record:
        messagebox.showinfo("Info", f"No records found for Work ID: {work_id}")
        return
            
    for item in self.search_tree.get_children():
        self.search_tree.delete(item)
        
    updated_at = record.get('updated_at', '')
    if updated_at:
        try:
            dt = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")
        except:
            formatted_date = updated_at
    else:
        formatted_date = 'Not available'
        
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
    
    self.tab_control.select(self.search_tab)

def load_project_data(self, work_id):
    """Load project data into the form"""
    from fromEvent.database_operations import load_from_db
    record = load_from_db(work_id)
    if not record:
        messagebox.showerror("Error", f"Record with Work ID {work_id} not found")
        return
    
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
    
    if record['setup_date']:
        try:
            if isinstance(record['setup_date'], str):
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
    
    from fromEvent.table_operations import clear_table, add_table_row
    clear_table(self.table_entries)
    
    for _ in range(len(record.get('inventory_items', [])) - len(self.table_entries)):
        add_table_row(self.scrollable_frame, self.table_entries, self.headers, 
                     self.original_column_widths, self.status_options, self.canvas)
    
    for i, item in enumerate(record.get('inventory_items', [])):
        if i >= len(self.table_entries):
            break
                
        row = self.table_entries[i]
        fields = [
            'zone_active', 'sno', 'name', 'description', 
            'quantity', 'comments', 'total', 'unit', 
            'per_unit_power', 'total_power', 'status', 'poc', 'RecQty'
        ]
        
        for col, field in enumerate(fields):
            if col < len(row):
                if col == 10:
                    row[col].set(item.get(field, self.status_options[0]))
                else:
                    row[col].delete(0, tk.END)
                    value = str(item.get(field, ''))
                    row[col].insert(0, value)
    
    self.tab_control.select(0)
    
    from fromEvent.new_event_entry import set_fields_readonly
    set_fields_readonly(self, True)
    self.edit_btn.config(state=tk.NORMAL)
    self.update_btn.config(state=tk.DISABLED)
