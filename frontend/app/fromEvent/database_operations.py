from common_imports import *
from api_request.from_event_inventory_request import (
    create_to_return_inventory_list,
    load_submitted_project_return_from_db,
    update_submitted__return_project_in_db,
    search_return_details_by_id
)

def initialize_db(db_file):
    """Initialize the JSON database file if it doesn't exist"""
    if not os.path.exists(db_file):
        with open(db_file, 'w') as f:
            json.dump([], f)

def save_to_db(data):
    """Save data to the database via API"""
    try:
        work_id = data['work_id']
        try:
            existing_records = search_return_details_by_id(work_id)
            if existing_records:
                if not update_submitted__return_project_in_db(work_id, data):
                    raise Exception("Failed to update record via API")
                return True
        except Exception as e:
            logger.warning(f"Project check failed, attempting create: {str(e)}")

        api_response = create_to_return_inventory_list(data)
        logger.info(f"New record created via API: {api_response}")
        return True
    except Exception as e:
        logger.error(f"Failed to save to database: {str(e)}")
        return False

def load_from_db(work_id=None):
    """Load data from API only"""
    try:
        if work_id:
            records = search_return_details_by_id(work_id)
            return records[0] if records else None
        else:
            records = load_submitted_project_return_from_db()
            if records:
                return sorted(records, key=lambda x: x.get('updated_at', ''), reverse=True)
            return []
    except Exception as e:
        logger.error(f"Failed to load from database: {str(e)}")
        return None
