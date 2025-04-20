#  frontend/app/utils/inventory_utils.py

import requests
from typing import List, Dict
from datetime import datetime, timedelta, date
import logging
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from config import *

# Format a single  inventory item to match the table headers
def format_wastage_inventory_item(item: Dict, include_timestamps: bool = False) -> Dict:
    """Format a single  inventory item from Redis search result with enhanced field mapping."""
    try:
        # Extract data from either the root or nested 'data' field
        item_data = item.get('data', item)
        
        # Handle date formatting
        def format_date(date_str):
            if not date_str:
                return "N/A"
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
            except:
                return date_str  # Return original if parsing fails

        formatted = {
            "id": str(item_data.get("id", "")),
            "sno": str(item_data.get("sno", "N/A")),
            "assign_to": str(item_data.get("assign_to", item_data.get("poc", "N/A"))),
            "employee_name": str(item_data.get("employee_name", "N/A")),
            "inventory_id": str(item_data.get("inventory_id", "N/A")).upper(),
            "project_id": str(item_data.get("project_id", "N/A")).upper(),
            "product_id": str(item_data.get("product_id", "N/A")).upper(),
            "inventory_name": str(item_data.get("inventory_name", item_data.get("name", "N/A"))),
            "description": str(item_data.get("description", "N/A")),
            "quantity": str(item_data.get("quantity", "N/A")),
            "status": str(item_data.get("status", "N/A")).capitalize(),
            
            "receive_date": format_date(item_data.get("receive_date", item_data.get("receive_date"))),
            "receive_by": format_date(item_data.get("receive_by")),
            "check_status": str(item_data.get("check_status", "N/A")),
            "location": str(item_data.get("location", item_data.get("location", "N/A"))),
            "project_name": str(item_data.get("comment", item_data.get("project_name", "N/A"))),
            "event_date": format_date(item_data.get("event_date")),
            "comment": str(item_data.get("comment", "N/A")),
            "zone_activity": str(item_data.get("zone_activity", item_data.get("zone_active", "N/A"))),
            "wastage_barcode": str(item_data.get("wastage_barcode", "N/A")),
            "wastage_barcode_image_url": str(item_data.get("wastage_barcode_image_url", "N/A")),
            "wastage_reason": str(item_data.get("wastage_reason", "N/A")),
            "wastage_date": format_date(item_data.get("wastage_date")),
            "wastage_approved_by": str(item_data.get("wastage_approved_by", "N/A")),
            "wastage_status": str(item_data.get("wastage_status", "N/A")),
        }

        if include_timestamps:
            formatted.update({
                "created_at": item_data.get("created_at", ""),
                "updated_at": item_data.get("updated_at", "")
            })

        return formatted

    except Exception as e:
        logger.error(f"Error formatting inventory item: {e}\nItem data: {item_data}")
        return {
            "error": f"Formatting error: {str(e)}",
            "raw_data": item_data
        }