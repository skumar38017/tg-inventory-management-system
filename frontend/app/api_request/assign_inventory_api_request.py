# front-end/app/api_request/assign_inventory_api_request.py

from common_imports import *

import logging

logger = logging.getLogger(__name__)

# Format a single assigned inventory item to match the table headers
def format_assigned_inventory_item(item: Dict, include_timestamps: bool = False) -> Dict:
    """Format a single assigned inventory item from Redis search result with enhanced field mapping."""
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
            "assigned_to": str(item_data.get("assign_to", item_data.get("poc", "N/A"))),
            "employee_name": str(item_data.get("employee_name", "N/A")),
            "inventory_id": str(item_data.get("inventory_id", "N/A")).upper(),
            "project_id": str(item_data.get("project_id", "N/A")).upper(),
            "product_id": str(item_data.get("product_id", "N/A")).upper(),
            "inventory_name": str(item_data.get("inventory_name", item_data.get("name", "N/A"))),
            "description": str(item_data.get("description", "N/A")),
            "quantity": str(item_data.get("quantity", "N/A")),
            "status": str(item_data.get("status", "N/A")).capitalize(),
            
            "assigned_date": format_date(item_data.get("assigned_date", item_data.get("event_date"))),
            "submission_date": format_date(item_data.get("submission_date")),
            "purpose_reason": str(item_data.get("purpose_reason", "N/A")),
            "assigned_by": str(item_data.get("assign_by", item_data.get("submitted_by", "N/A"))),
            "comments": str(item_data.get("comment", item_data.get("comments", "N/A"))),
            "assignment_return_date": format_date(item_data.get("assignment_return_date")),
            "assignment_barcode": str(item_data.get("assignment_barcode", "N/A")),
            "zone_activity": str(item_data.get("zone_activity", item_data.get("zone_active", "N/A"))),
            "location": str(item_data.get("location", "N/A")),
            "client_name": str(item_data.get("client_name", "N/A"))
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


def search_assigned_inventory_by_id(
    inventory_id: str = None, 
    project_id: str = None, 
    employee_name: str = None, 
    product_id: str = None
) -> List[Dict]:
    """
    Enhanced search function for assigned inventory with better parameter handling and error reporting.
    
    Args:
        inventory_id: Inventory ID (with or without INV prefix)
        project_id: Project ID (with or without PRJ prefix)
        employee_name: Employee name (partial matches supported)
        product_id: Product ID (with or without PRD prefix)
    
    Returns:
        List of properly formatted inventory items
        Empty list on error with error message shown to user
    """
    try:
        # Normalize and validate parameters
        params = {}
        
        def normalize_id(id_value, prefix):
            """Normalize ID by removing prefix if present and ensuring uppercase"""
            if not id_value:
                return None
            id_value = str(id_value).strip().upper()
            return id_value.replace(prefix, "") if id_value.startswith(prefix) else id_value

        if inventory_id:
            params['inventory_id'] = normalize_id(inventory_id, "INV")
        if project_id:
            params['project_id'] = normalize_id(project_id, "PRJ")
        if product_id:
            params['product_id'] = normalize_id(product_id, "PRD")
        if employee_name:
            params['employee_name'] = employee_name.strip()

        if not params:
            raise ValueError("Please provide at least one search parameter")

        # API request with timeout
        response = make_api_request(
            "GET", 
            "search-assigned-inventory/", 
            params=params,
            timeout=30  # 30 second timeout
        )
        
        # Check for empty response
        if not response.content:
            raise ValueError("Server returned empty response")

        response.raise_for_status()
        results = response.json()

        # Process and validate results
        if not isinstance(results, list):
            raise ValueError(f"Unexpected response format. Expected list, got {type(results)}")

        formatted_results = []
        error_count = 0
        
        for item in results:
            formatted = format_assigned_inventory_item(item)
            if "error" not in formatted:
                formatted_results.append(formatted)
            else:
                error_count += 1

        if error_count:
            logger.warning(f"Skipped {error_count} malformed items in search results")

        if not formatted_results:
            messagebox.showinfo("No Results", "No matching inventory items found")
            
        return formatted_results

    except requests.exceptions.Timeout:
        error_msg = "Search timed out. Please try again later."
        logger.error(error_msg)
        messagebox.showerror("Timeout Error", error_msg)
        return []
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error during search: {str(e)}"
        if hasattr(e, 'response') and e.response:
            try:
                error_detail = e.response.json().get('detail', 'No details')
                error_msg += f"\nServer response: {error_detail}"
            except:
                error_msg += f"\nStatus code: {e.response.status_code}"
        logger.error(error_msg)
        messagebox.showerror("Search Error", error_msg)
        return []
    except ValueError as ve:
        logger.error(f"Invalid search parameters: {ve}")
        messagebox.showwarning("Invalid Search", str(ve))
        return []
    except Exception as e:
        logger.error(f"Unexpected search error: {str(e)}\n{traceback.format_exc()}")
        messagebox.showerror("Error", "An unexpected error occurred during search")
        return []


def load_submitted_assigned_inventory() -> List[Dict]:
    try:
        response = make_api_request("GET", "list-added-assign-inventory/")
        response.raise_for_status()

        formatted_data = [
            format_assigned_inventory_item(item, include_timestamps=True)
            for item in response.json()
        ]

        formatted_data.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return formatted_data

    except Exception as e:
        logger.error(f"Could not fetch submitted forms: {str(e)}")
        messagebox.showerror("Error", "Could not fetch submitted forms")
        return []
        
def show_all_assigned_inventory_from_db() -> List[Dict]:
    try:
        response = make_api_request("GET", "show-all-assign-inventory/")
        response.raise_for_status()

        formatted_data = [
            format_assigned_inventory_item(item, include_timestamps=True)
            for item in response.json()
        ]
        formatted_data.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return formatted_data

    except Exception as e:
        logger.error(f"Could not fetch assigned inventory: {str(e)}")
        messagebox.showerror("Error", "Could not fetch assigned inventory")
        return []
    
def submit_assigned_inventory(data: Dict) -> bool:
    try:
        # Prepare payload for each assignment
        assignments = []
        for assignment in data.get('assignments', []):
            payload = {
                "assign_to": assignment.get("assign_to", ""),
                "employee_name": assignment.get("employee_name", ""),
                "sno": assignment.get("sno", ""),
                "zone_activity": assignment.get("zone_activity", ""),
                "inventory_id": assignment.get("inventory_id", ""),
                "project_id": assignment.get("project_id", ""),
                "product_id": assignment.get("product_id", ""),
                "inventory_name": assignment.get("inventory_name", ""),
                "description": assignment.get("description", ""),
                "quantity": assignment.get("quantity", "1"),
                "status": assignment.get("status", "assigned"),
                "purpose_reason": assignment.get("purpose_reason", ""),
                "assigned_date": assignment.get("assigned_date", datetime.now().strftime('%Y-%m-%d')),
                "assign_by": assignment.get("assign_by", ""),
                "comment": assignment.get("comment", ""),
                "assignment_return_date": assignment.get("assignment_return_date", 
                    (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d'))
            }
            assignments.append(payload)
            logger.debug(f"Submitting payload: {json.dumps(payload, indent=2)}")

        # Submit each assignment individually
        for payload in assignments:
            response = make_api_request("POST", "create-assign-inventory/", json=payload)
            response.raise_for_status()
            
        return True

    except requests.RequestException as e:
        logger.error(f"API request failed to {e.request.url}: {e}")
        logger.error(f"Response content: {e.response.text if e.response else 'No response'}")
        messagebox.showerror("Error", f"Failed to submit data: {e}")
        return False
    except Exception as e:
        
        logger.error(f"Unexpected error during submission: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return False
            
# UPDATE: update/edit an existing Assigned Inventory by [EmployeeName, InventoryID]
def update_assigned_inventory(employee_name: str, inventory_id: str, data: Dict) -> bool:
    """Update assigned inventory using employee_name and inventory_id"""
    try:
        # Prepare only the allowed fields for update
        update_data = {
            "assign_to": data.get("assign_to", ""),
            "sno": data.get("sno", ""),
            "zone_activity": data.get("zone_activity", ""),
            "description": data.get("description", ""),
            "quantity": data.get("quantity", "1"),
            "status": data.get("status", "assigned"),
            "purpose_reason": data.get("purpose_reason", ""),
            "assign_by": data.get("assign_by", ""),
            "comment": data.get("comment", ""),
            "submission_date": data.get("submission_date", datetime.now().isoformat()),
            "assigned_date": data.get("assigned_date", datetime.now().strftime('%Y-%m-%d')),
            "assignment_return_date": data.get("assignment_return_date", (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        }
        
        # Remove empty date fields
        for date_field in ['submission_date', 'assigned_date', 'assignment_return_date']:
            if not update_data[date_field]:
                update_data.pop(date_field)
        
        logger.debug(f"Sending update data: {update_data}")
        
        response = make_api_request(
            "PUT", 
            f"update-assigned-inventory/{employee_name}/{inventory_id}/",
            json=update_data,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return True
    
    except requests.HTTPError as e:
        if e.response.status_code == 422:
            validation_errors = e.response.json().get('detail', 'Unknown validation error')
            logger.error(f"Validation errors: {validation_errors}")
        logger.error(f"Failed to update assigned inventory: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during update: {e}")
        return False
    
def get_assigned_inventory_by_id(inventory_id: str) -> Dict:
    try:
        response = make_api_request("GET", f"get-assigned-inventory/{inventory_id}/")
        response.raise_for_status()
        return format_assigned_inventory_item(response.json())

    except requests.RequestException as e:
        logger.error(f"Failed to fetch assigned inventory: {e}")
        messagebox.showerror("Error", "Could not fetch assigned inventory data")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return {}  
    
def delete_assigned_inventory(record_id: str) -> bool:
    """Delete an assigned inventory record by its ID"""
    try:
        response = make_api_request(
            "DELETE",
            f"delete-assigned-inventory/{record_id}/"
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to delete assigned inventory: {e}")
        messagebox.showerror("Error", "Could not delete assigned inventory data")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}")
        messagebox.showerror("Error", "An unexpected error occurred")
        return False