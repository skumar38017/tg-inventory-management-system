from utils.common_header import create_header_section, update_clock
from common_imports import *
from utils.universal_font_box_size import universal_font_box_size

def configure_treeviews(assigned_tree, recent_tree, new_entry_tree, headers):
    """Configure columns for all treeviews"""
    default_font = font.nametofont("TkDefaultFont")
    
    for tree in [assigned_tree, recent_tree, new_entry_tree]:
        tree['columns'] = headers
        tree['show'] = 'headings'
        
        for col, header in enumerate(headers):
            tree.heading(col, text=header, anchor='center')
            tree.column(col, width=default_font.measure(header) + 150, 
                    stretch=False, anchor='center')
