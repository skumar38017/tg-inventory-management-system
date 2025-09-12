# ~/app/utils/pagination.py

class Pagination:
    def __init__(self, total_items, page_size=20):
        self.total_items = total_items
        self.page_size = page_size
        self.current_page = 0
        
    @property
    def total_pages(self):
        return (self.total_items + self.page_size - 1) // self.page_size
    
    def get_page_data(self, data, page=None):
        if page is not None:
            self.current_page = page
        
        start = self.current_page * self.page_size
        end = start + self.page_size
        return data[start:end]
    
    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        return self.current_page
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
        return self.current_page
    
    def go_to_page(self, page):
        if 0 <= page < self.total_pages:
            self.current_page = page
        return self.current_page
    
    def get_page_info(self):
        return {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'page_size': self.page_size,
            'total_items': self.total_items,
            'start_item': self.current_page * self.page_size + 1,
            'end_item': min((self.current_page + 1) * self.page_size, self.total_items)
        }
