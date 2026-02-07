from common_imports import *
from utils.universal_font_box_size import universal_font_box_size
from homePage.entry_update_pop_window import UpdatePopUpWindow

def create_inventory_list_tab(notebook, inventory_listbox_ref, from_date_entry_ref, to_date_entry_ref, 
                               filter_by_date_range, update_main_inventory_list, upload_inventory_with_message, 
                               update_inventory_list, root_window):
    """Create the Inventory List tab with filters and treeview"""
    inventory_frame = tk.Frame(notebook, bg='white')
    notebook.add(inventory_frame, text="Inventory List")
    
    date_filter_frame = tk.Frame(inventory_frame, bg='#ecf0f1', relief='raised', bd=1)
    date_filter_frame.pack(fill="x", pady=8, padx=8)
    
    left_frame = tk.Frame(date_filter_frame, bg='#ecf0f1')
    left_frame.pack(side="left", fill="x", expand=True, padx=12, pady=8)
    
    from_date_entry, to_date_entry = create_date_range_picker(left_frame, bg_color='#ecf0f1', start_column=0, row=0)
    from_date_entry_ref['entry'] = from_date_entry
    to_date_entry_ref['entry'] = to_date_entry
    
    filter_btn = tk.Button(left_frame, text="Filter", command=filter_by_date_range,
                         font=(universal_font_box_size.qr_barcode_header_font_family, 12, 'bold'), height=1, width=12,
                         bg='#2c3e50', fg='white', relief='flat',
                         activebackground='#34495e', activeforeground='white')
    filter_btn.grid(row=0, column=4, padx=5)
    
    show_all_btn = tk.Button(left_frame, text="Show All", command=update_main_inventory_list,
                           font=(universal_font_box_size.qr_barcode_header_font_family, 12, 'bold'), height=1, width=12,
                           bg='#95a5a6', fg='white', relief='flat',
                           activebackground='#7f8c8d', activeforeground='white')
    show_all_btn.grid(row=0, column=5, padx=5)
    
    right_frame = tk.Frame(date_filter_frame, bg='#ecf0f1')
    right_frame.pack(side="right", fill="x", padx=12, pady=8)

    update_btn = UpdatePopUpWindow.create_update_button(right_frame, root_window=root_window)
    update_btn.pack(side="right", padx=5)

    upload_btn = tk.Button(
        right_frame, 
        text="Upload", 
        command=upload_inventory_with_message,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_large, 'bold'),
        height=1, width=12,
        bg='#34495e', fg='white', relief='flat',
        activebackground='#2c3e50', activeforeground='white'
    )
    upload_btn.pack(side="right", padx=5)

    sync_btn = tk.Button(
        right_frame, 
        text="Sync", 
        command=update_inventory_list,
        font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.button_width_large, 'bold'),
        height=1, width=12,
        bg='#7f8c8d', fg='white', relief='flat',
        activebackground='#95a5a6', activeforeground='white'
    )
    sync_btn.pack(side="right", padx=5)

    UpdatePopUpWindow.create_update_button(inventory_frame, root_window=root_window)
    
    separator = ttk.Separator(inventory_frame, orient='horizontal')
    separator.pack(fill="x", pady=8, padx=8)
        
    list_container = tk.Frame(inventory_frame, bg='white', relief='sunken', bd=1)
    list_container.pack(fill="both", expand=True, padx=8, pady=(0,8))
    
    h_scrollbar = tk.Scrollbar(list_container, orient="horizontal")
    h_scrollbar.pack(side="bottom", fill="x")
    
    v_scrollbar = tk.Scrollbar(list_container, orient="vertical")
    v_scrollbar.pack(side="right", fill="y")
    
    columns = ['ID','Serial No.', 'InventoryID', 'ProductID', 'Name', 'Material', 'Total Quantity', 
               'Manufacturer', 'Purchase Dealer', 'Purchase Date', 'Purchase Amount', 
               'Repair Quantity', 'Repair Cost', 'On Rent', 'Vendor Name', 'Total Rent', 
               'Rented Returned', 'Returned Date', 'On Event', 'In Office', 
               'In Warehouse', 'Issued Qty', 'Balance Qty', 'Bar Code', 'Barcode URL', 
               'QrCodeUrl', 'Created At', 'Updated At', 'Submitted by']
    
    listbox_height = universal_font_box_size.button_width_medium
    inventory_listbox = ttk.Treeview(list_container, columns=columns, show='headings', height=listbox_height)
    
    uniform_width = 500
    for col in columns:
        inventory_listbox.heading(col, text=col, anchor="center")
        inventory_listbox.column(col, width=uniform_width, minwidth=uniform_width, anchor='center', stretch=False)
    
    def sync_header_scroll(*args):
        inventory_listbox.xview(*args)
    
    h_scrollbar.config(command=sync_header_scroll)
    inventory_listbox.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
    v_scrollbar.config(command=inventory_listbox.yview)
    
    inventory_listbox.pack(side="left", fill="both", expand=True)
    
    def scroll_left(event):
        sync_header_scroll("scroll", -1, "units")
        return "break"
    
    def scroll_right(event):
        sync_header_scroll("scroll", 1, "units")
        return "break"
    
    def scroll_up(event):
        inventory_listbox.yview_scroll(-50, "units")
        return "break"
    
    def scroll_down(event):
        inventory_listbox.yview_scroll(50, "units")
        return "break"
    
    inventory_listbox.bind('<Left>', scroll_left)
    inventory_listbox.bind('<Right>', scroll_right)
    inventory_listbox.bind('<Up>', scroll_up)
    inventory_listbox.bind('<Down>', scroll_down)
    inventory_listbox.focus_set()
    
    style = ttk.Style()
    style.configure('Treeview', font=(universal_font_box_size.qr_barcode_title_font_family))
    style.configure("Treeview", rowheight=universal_font_box_size.input_height)
    style.configure('Treeview.Heading', font=(universal_font_box_size.qr_barcode_title_font_family))
    style.configure('Treeview.Heading', rowheight=universal_font_box_size.input_height)
    
    style.configure("Treeview", 
                   relief="solid", 
                   borderwidth=1,
                   fieldbackground="white",
                   rowheight=35)
    style.configure("Treeview.Heading", 
                   relief="solid", 
                   borderwidth=1,
                   background="#d4e6f1",
                   foreground="black",
                   anchor="center")

    inventory_listbox.tag_configure('evenrow', background='#f5f5f5')
    inventory_listbox.tag_configure('oddrow', background='#ffffff')
    
    setup_modern_scrolling(inventory_listbox)
    
    inventory_listbox_ref['listbox'] = inventory_listbox
    
    return inventory_frame
