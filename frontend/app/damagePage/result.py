from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def setup_results_ui(parent, display_names, on_select_callback):
    """Setup results treeview section"""
    results_frame = tk.LabelFrame(parent, text="Results", padx=5, pady=5,
                                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    tree = ttk.Treeview(results_frame, columns=display_names, show="headings")
    vsb = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    
    for col, name in enumerate(display_names):
        tree.heading(col, text=name)
        tree.column(col, width=400, minwidth=250)
    
    tree.bind("<<TreeviewSelect>>", on_select_callback)
    
    results_frame.grid_rowconfigure(0, weight=1)
    results_frame.grid_columnconfigure(0, weight=1)
    
    return results_frame, tree

def display_results(tree, results, fields):
    """Display results in treeview"""
    tree.delete(*tree.get_children())
    if results:
        for item in results:
            values = [item.get(field, "") for field in fields]
            tree.insert("", tk.END, values=values)
