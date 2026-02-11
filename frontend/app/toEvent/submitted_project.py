from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def setup_submitted_tab(submitted_tab, parent_instance):
    """Setup the tab for submitted projects"""
    frame = tk.Frame(submitted_tab)
    frame.pack(fill="both", expand=True)

    # Treeview for submitted projects
    submitted_tree = ttk.Treeview(frame, height=10,
                                     columns=("WorkID", "Employee", "Location", "ProjectName", 
                                             "Client", "SetupDate", "EventDate", "LastUpdated"),
                                     show="headings")
    
    # Configure columns
    submitted_tree.heading("WorkID", text="Work ID")
    submitted_tree.heading("Employee", text="Employee")
    submitted_tree.heading("Location", text="Location")
    submitted_tree.heading("ProjectName", text="Project Name")
    submitted_tree.heading("Client", text="Client Name")
    submitted_tree.heading("SetupDate", text="Setup Date")
    submitted_tree.heading("EventDate", text="Event Date")
    submitted_tree.heading("LastUpdated", text="Last Updated")
    
    submitted_tree.column("WorkID", width=100)
    submitted_tree.column("Employee", width=150)
    submitted_tree.column("Location", width=100)
    submitted_tree.column("ProjectName", width=150)
    submitted_tree.column("Client", width=150)
    submitted_tree.column("SetupDate", width=100)
    submitted_tree.column("EventDate", width=100)
    submitted_tree.column("LastUpdated", width=150)

    # Scrollbars
    y_scroll = ttk.Scrollbar(frame, orient="vertical", command=submitted_tree.yview)
    submitted_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=y_scroll.set)

    # Grid layout
    submitted_tree.pack(side="left", fill="both", expand=True)
    y_scroll.pack(side="right", fill="y")

    # Double-click to load project
    submitted_tree.bind("<Double-1>", lambda e: load_submitted_project(parent_instance, submitted_tree))
    
    return submitted_tree

def load_submitted_project(parent_instance, submitted_tree):
    """Load project from submitted tab when double-clicked"""
    selected = submitted_tree.selection()
    if selected:
        item = submitted_tree.item(selected)
        work_id = item['values'][0]
        parent_instance.load_project_data(work_id)
