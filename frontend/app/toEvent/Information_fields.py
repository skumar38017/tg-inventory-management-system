from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def create_information_fields(window, parent_instance):
    """Create information fields section with all input fields and buttons"""
    info_frame = tk.Frame(window)
    info_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
    
    entries = {}
    
    tk.Label(info_frame, text="Project ID (Search):", 
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=0, column=0, sticky='e', padx=2)
    entries['project_id'] = tk.Entry(info_frame, 
                               font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                               width=universal_font_box_size.search_entry_width, justify='center')
    entries['project_id'].grid(row=0, column=1, sticky='w', padx=2)
            
    fetch_btn = tk.Button(info_frame, text="Fetch", command=parent_instance.fetch_record,
                             font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    fetch_btn.grid(row=0, column=2, sticky='w', padx=5)
    
    edit_btn = tk.Button(info_frame, text="Edit", command=parent_instance.edit_record,
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'), state=tk.NORMAL)
    edit_btn.grid(row=0, column=3, sticky='w', padx=5)
    
    update_btn = tk.Button(info_frame, text="Update", command=parent_instance.update_record,
                              font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'), state=tk.DISABLED)
    update_btn.grid(row=0, column=4, sticky='w', padx=5)

    add_btn = tk.Button(info_frame, text="New Entry", command=parent_instance.new_button_click,
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    add_btn.grid(row=0, column=5, sticky='w', padx=5)

    clear_btn = tk.Button(info_frame, text="Clear", command=parent_instance.clear_form,
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    clear_btn.grid(row=0, column=6, sticky='w', padx=5)

    refresh_btn = tk.Button(info_frame, text="Refresh", command=parent_instance.refresh_data,
                               font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size, 'bold'))
    refresh_btn.grid(row=0, column=7, sticky='w', padx=5)

    tk.Label(info_frame, text="Employee Name:", 
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=1, column=0, sticky='e', padx=2, pady=(5, 2))
    entries['employee_name'] = tk.Entry(info_frame, 
                                  font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                                  width=universal_font_box_size.search_entry_width, justify='center')
    entries['employee_name'].grid(row=1, column=1, sticky='w', padx=2, pady=(5, 2))

    tk.Label(info_frame, text="Location:", 
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=1, column=2, sticky='e', padx=2, pady=(5, 2))
    entries['location'] = tk.Entry(info_frame, 
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                            width=universal_font_box_size.search_entry_width, justify='center')
    entries['location'].grid(row=1, column=3, sticky='w', padx=2, pady=(5, 2))

    tk.Label(info_frame, text="Client Name:", 
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=1, column=4, sticky='e', padx=2, pady=(5, 2))
    entries['client_name'] = tk.Entry(info_frame, 
                                font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                                width=universal_font_box_size.search_entry_width, justify='center')
    entries['client_name'].grid(row=1, column=5, sticky='w', padx=2, pady=(5, 2))

    tk.Label(info_frame, text="Project Name:", 
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=2, column=0, sticky='e', padx=2, pady=(5, 2))
    entries['project_name'] = tk.Entry(info_frame, 
                                 font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                                 width=universal_font_box_size.search_entry_width, justify='center')
    entries['project_name'].grid(row=2, column=1, sticky='w', padx=2, pady=(5, 2))

    tk.Label(info_frame, text="Setup Date:", 
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=2, column=2, sticky='e', padx=2, pady=(5, 2))
    entries['setup_date'] = DateEntry(info_frame, 
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                            width=universal_font_box_size.search_entry_width-1,
                            date_pattern='yyyy-mm-dd',
                            background='darkblue',
                            foreground='white',
                            borderwidth=2, justify='center')
    entries['setup_date'].grid(row=2, column=3, sticky='w', padx=2, pady=(5, 2))

    tk.Label(info_frame, text="Event Date:", 
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=2, column=4, sticky='e', padx=2, pady=(5, 2))
    entries['event_date'] = DateEntry(info_frame, 
                            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                            width=universal_font_box_size.search_entry_width-1,
                            date_pattern='yyyy-mm-dd',
                            background='darkblue',
                            foreground='white',
                            borderwidth=2, justify='center')
    entries['event_date'].grid(row=2, column=5, sticky='w', padx=2, pady=(5, 2))

    tk.Label(info_frame, text="Current Work ID:", 
            font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size)).grid(row=2, column=6, sticky='e', padx=2, pady=(5, 2))
    entries['work_id'] = tk.Entry(info_frame, 
                           font=(universal_font_box_size.qr_barcode_header_font_family, universal_font_box_size.search_entry_font_size), 
                           width=universal_font_box_size.search_entry_width, state='readonly', justify='center')
    entries['work_id'].grid(row=2, column=7, sticky='w', padx=2, pady=(5, 2))
    
    return entries, fetch_btn, edit_btn, update_btn
