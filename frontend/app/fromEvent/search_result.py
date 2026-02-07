from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def setup_search_tab(search_tab, parent_instance):
    """Setup the tab for search results"""
    frame = tk.Frame(search_tab)
    frame.pack(fill="both", expand=True)

    # Treeview for search results
    search_tree = ttk.Treeview(frame, height=10,
                                  columns=("WorkID", "ProjectName", "Employee", "Location", 
                                          "Client", "SetupDate", "EventDate", "LastUpdated"),
                                  show="headings")
    
    # Configure columns
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

    # Scrollbars
    y_scroll = ttk.Scrollbar(frame, orient="vertical", command=search_tree.yview)
    search_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=y_scroll.set)

    # Grid layout
    search_tree.pack(side="left", fill="both", expand=True)
    y_scroll.pack(side="right", fill="y")

    # Double-click to load project
    search_tree.bind("<Double-1>", lambda e: load_search_result(parent_instance, search_tree))
    
    return search_tree

def load_search_result(parent_instance, search_tree):
    """Load project from search results when double-clicked"""
    selected = search_tree.selection()
    if selected:
        item = search_tree.item(selected)
        work_id = item['values'][0]
        parent_instance.load_project_data(work_id)
