# ~/app/utils/pagination.py

class Pagination:
    def __init__(self):
        self.current_page = 0
        self.page_size = 20
        
    def get_page_data(self, data):
        start = self.current_page * self.page_size
        end = start + self.page_size
        return data[start:end]
    
    def next_page(self):
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
