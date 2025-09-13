# ~/app/schema/pagination.py
from app.schema.common_schema import *

class Pagination(BaseValidators, BaseModel):
    start_page: int = Field(1, ge=1)
    end_page: int = Field(1, ge=1)
    total_count: int = Field(0, ge=0)
    total_pages: int = Field(0, ge=0)
    data: List[Any] = []
