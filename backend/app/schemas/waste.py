from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class WasteRecordCreate(BaseModel):
    category: str = Field(..., pattern="^(Yellow|Red|White|Blue)$")
    waste_type: str = Field(..., min_length=2, max_length=120)
    quantity: float = Field(..., gt=0.0, le=1000.0)
    unit: str = Field(default="kg", max_length=10)
    notes: Optional[str] = Field(default=None, max_length=500)

class WasteRecordResponse(BaseModel):
    id: int
    hospital_id: int
    category: str
    waste_type: str
    quantity: float
    unit: str
    notes: Optional[str] = None
    is_scheduled: bool
    created_at: datetime

    class Config:
        from_attributes = True
