from common_imports import *

def refresh_all_data(assigned_section, recent_section):
    """Refresh all data in the window"""
    try:
        assigned_section.refresh_assigned_inventory_list()
        recent_section.load_recent_submissions()
        messagebox.showinfo("Success", "Data refreshed successfully")
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        messagebox.showerror("Error", "Failed to refresh data")
