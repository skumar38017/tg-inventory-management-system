import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union
import math

def paginate_data(
    data: Union[List[Dict], pd.DataFrame], 
    page: int = 1, 
    per_page: int = 20
) -> Dict[str, Any]:
    """
    Robust pagination system for any data type
    
    Args:
        data: List of dictionaries or pandas DataFrame
        page: Page number (starts from 1)
        per_page: Items per page (default 20)
    
    Returns:
        Dict with paginated data and metadata
    """
    # Convert to DataFrame if it's a list
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()
    
    # Calculate pagination metadata
    total_items = len(df)
    total_pages = math.ceil(total_items / per_page) if total_items > 0 else 1
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages))
    
    # Calculate start and end indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Get paginated data
    paginated_df = df.iloc[start_idx:end_idx]
    
    # Convert back to list of dicts if original was list
    if isinstance(data, list):
        paginated_data = paginated_df.to_dict('records')
    else:
        paginated_data = paginated_df
    
    return {
        "data": paginated_data,
        "pagination": {
            "current_page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None
        }
    }
