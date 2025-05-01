from pydantic import BaseModel, Field
from datetime import datetime

class TimeSlot(BaseModel):
    start_time: datetime = Field(..., example="2025-04-20T13:00:00Z")
    end_time: datetime = Field(..., example="2025-04-20T14:00:00Z")

class TimeSlotIn(BaseModel): # store according to ISO 8601
    start_time: str = Field(..., example="2025-04-20T13:00:00Z")
    end_time:   str = Field(..., example="2025-04-20T14:00:00Z")

class TimeSlotOut(TimeSlotIn):
    slot_id: str