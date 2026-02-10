from common_imports import *
from api_request.damage_inventory_api_request import show_all_wastage_inventory

def refresh_data(tree, fields):
    """Refresh all data from API"""
    results = show_all_wastage_inventory()
    from damagePage.result import display_results
    display_results(tree, results, fields)
    logger.info("Data refreshed")

def on_tree_select(tree, fields, event):
    """Handle selection from treeview"""
    selected = tree.focus()
    if selected:
        values = tree.item(selected, "values")
        if values:
            logger.info(f"Item selected: {values[fields.index('inventory_id')]}")
        return selected, values
    return None, None
