from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class TableCreate(BaseModel):
    table_number: str
    capacity: int
    location: Optional[str] = None

class TableUpdate(BaseModel):
    capacity: Optional[int] = None
    location: Optional[str] = None

class TableResponse(BaseModel):
    id: UUID
    table_number: str
    capacity: int
    location: Optional[str]
    is_occupied: bool

    model_config = {
    "from_attributes": True
    }