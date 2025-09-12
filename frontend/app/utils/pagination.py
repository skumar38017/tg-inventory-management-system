# ~/app/utils/pagination.py

try:
    import numpy as np
    import pandas as pd
    HAS_NUMPY_PANDAS = True
except ImportError:
    HAS_NUMPY_PANDAS = False

class Pagination:
    def __init__(self, page_size=20):
        self.page_size = page_size
        self.current_page = 0
        
    def get_page_data(self, data, page=None):
        if page is not None:
            self.current_page = page
        
        start = self.current_page * self.page_size
        end = start + self.page_size
        
        # Use pandas/numpy for fast slicing if available and data is large
        if HAS_NUMPY_PANDAS and len(data) > 1000:
            if isinstance(data, (list, tuple)):
                data_array = np.array(data)
                return data_array[start:end].tolist()
            elif hasattr(data, 'iloc'):  # pandas DataFrame/Series
                return data.iloc[start:end]
        
        return data[start:end]
    
    def next_page(self, data):
        next_start = (self.current_page + 1) * self.page_size
        
        # Fast length check with numpy if available
        if HAS_NUMPY_PANDAS and hasattr(data, 'shape'):
            data_len = data.shape[0]
        else:
            data_len = len(data)
            
        if next_start < data_len:
            self.current_page += 1
        return self.current_page
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
        return self.current_page
    
    def go_to_page(self, page):
        if page >= 0:
            self.current_page = page
        return self.current_page
    
    def get_page_info(self, data):
        # Fast calculation with numpy if available
        if HAS_NUMPY_PANDAS and hasattr(data, 'shape'):
            total_items = data.shape[0]
        else:
            total_items = len(data)
            
        # Use numpy for fast math operations
        if HAS_NUMPY_PANDAS:
            total_pages = int(np.ceil(total_items / self.page_size)) if total_items > 0 else 1
            start_item = self.current_page * self.page_size + 1
            end_item = int(np.minimum((self.current_page + 1) * self.page_size, total_items))
        else:
            total_pages = (total_items + self.page_size - 1) // self.page_size if total_items > 0 else 1
            start_item = self.current_page * self.page_size + 1
            end_item = min((self.current_page + 1) * self.page_size, total_items)
        
        return {
            'current_page': self.current_page,
            'total_pages': total_pages,
            'page_size': self.page_size,
            'total_items': total_items,
            'start_item': start_item,
            'end_item': end_item,
            'has_next': (self.current_page + 1) * self.page_size < total_items,
            'has_prev': self.current_page > 0
        }
