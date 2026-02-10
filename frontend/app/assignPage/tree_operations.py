from common_imports import *

def auto_size_columns(tree, headers):
    """Automatically resize columns to fit content"""
    default_font = font.nametofont("TkDefaultFont")
    
    for col in range(len(headers)):
        max_width = default_font.measure(headers[col]) + 60
        
        for item in tree.get_children():
            item_text = tree.set(item, col)
            item_width = default_font.measure(item_text)
            if item_width > max_width:
                max_width = item_width + 60
        
        tree.column(col, width=max(min(max_width, 750), 400), stretch=False)

def bind_column_resize(trees, callback):
    """Bind column resize events to trees"""
    for tree in trees:
        tree.bind("<Map>", lambda e, t=tree: callback(t))
