# ~/app/schema/enum.py

from app.schema.common_schema import *

class StatusEnum(str, Enum):
    ASSIGNED = "assigned"
    RETURN = "returned"
