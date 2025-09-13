# ~/app/schema/common_schema.py

from app.utils.common_imports import *

import json
from typing import Optional, Union, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from app.utils.field_validators import BaseValidators
from app.utils.date_utils import UTCDateUtils
from app.schema.enum import StatusEnum

from app.schema.entry_inventory_schema import EntryInventoryOut, InventoryRedisOut
from app.schema.to_event_inventry_schma import ToEventRedisOut, ToEventInventoryOut, ToEventRedisUpdateOut, InventoryItemOut
from app.schema.assign_inventory_schema import AssignmentInventoryRedisOut
from app.models.wastege_inventory_model import WastageInventory