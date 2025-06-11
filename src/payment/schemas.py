from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional


# Match your SQLAlchemy Enum
class PaymentMethod(str, Enum):
    CARD = "card"
    CASH = "cash"
    POS = "pos"


# Base schema for shared fields
class PaymentBase(BaseModel):
    order_id: UUID
    customer_id: Optional[UUID]
    amount: Decimal
    method: PaymentMethod
    is_successful: bool = False


# Schema for creating a payment
class PaymentCreate(PaymentBase):
    pass


# Schema for updating a payment
class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = None
    method: Optional[PaymentMethod] = None
    is_successful: Optional[bool] = None
    customer_id: Optional[UUID] = None


# Schema for reading payment (return to API client)
class PaymentRead(PaymentBase):
    id: UUID
    paid_at: datetime

    class Config:
        orm_mode = True
