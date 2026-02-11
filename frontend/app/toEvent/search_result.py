from common_imports import *
from toEvent.database_operations import load_from_db

def setup_search_tab(search_tab, parent_instance):
    """Setup the tab for search results"""
    frame = tk.Frame(search_tab)
    frame.pack(fill="both", expand=True)

    search_tree = ttk.Treeview(frame, height=10,
                                  columns=("WorkID", "ProjectName", "Employee", "Location", 
                                          "Client", "SetupDate", "EventDate", "LastUpdated"),
                                  show="headings")
    
    search_tree.heading("WorkID", text="Work ID")
    search_tree.heading("ProjectName", text="Project Name")
    search_tree.heading("Employee", text="Employee")
    search_tree.heading("Location", text="Location")
    search_tree.heading("Client", text="Client")
    search_tree.heading("SetupDate", text="Setup Date")
    search_tree.heading("EventDate", text="Event Date")
    search_tree.heading("LastUpdated", text="Last Updated")
    
    search_tree.column("WorkID", width=100)
    search_tree.column("ProjectName", width=150)
    search_tree.column("Employee", width=150)
    search_tree.column("Location", width=100)
    search_tree.column("Client", width=150)
    search_tree.column("SetupDate", width=100)
    search_tree.column("EventDate", width=100)
    search_tree.column("LastUpdated", width=150)

    y_scroll = ttk.Scrollbar(frame, orient="vertical", command=search_tree.yview)
    search_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=y_scroll.set)

    search_tree.pack(side="left", fill="both", expand=True)
    y_scroll.pack(side="right", fill="y")

    search_tree.bind("<Double-1>", lambda e: load_search_result(parent_instance, search_tree))
    
    return search_tree

def load_search_result(parent_instance, search_tree):
    """Load project from search results when double-clicked"""
    selected = search_tree.selection()
    if selected:
        item = search_tree.item(selected)
        work_id = item['values'][0]
        parent_instance.load_project_data(work_id)

def fetch_record(parent_instance, project_id, search_tree, tab_control, search_tab):
    """Search records by Work ID and display in Search Results tab"""
    work_id = project_id.get().strip()
    if not work_id:
        messagebox.showwarning("Warning", "Please enter a Work ID to search")
        return
        
    record = load_from_db(work_id)
    
    if not record:
        messagebox.showinfo("Info", f"No records found for Work ID: {work_id}")
        return
            
    for item in search_tree.get_children():
        search_tree.delete(item)
        
    updated_at = record.get('updated_at', '')
    if updated_at:
        try:
            dt = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            formatted_date = dt.strftime("%Y-%m-%d %I:%M %p")
        except:
            formatted_date = updated_at
    else:
        formatted_date = 'Not available'
        
    search_tree.insert("", "end", values=(
        record['work_id'],
        record['project_name'],
        record['employee_name'],
        record['location'],
        record['client_name'],
        record['setup_date'],
        record['event_date'],
        formatted_date
    ))
    
    tab_control.select(search_tab)
