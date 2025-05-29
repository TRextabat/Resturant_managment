from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from enum import Enum
from datetime import datetime
from typing import Optional


class PaymentMethod(str, Enum):
    CARD = "card"
    CASH = "cash"
    POS = "pos"


class CreatePaymentRequest(BaseModel):
    order_id: UUID
    amount: Decimal = Field(..., gt=0)
    method: PaymentMethod


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    customer_id: Optional[UUID]
    amount: Decimal
    method: PaymentMethod
    is_successful: bool
    paid_at: datetime

    class Config:
        from_attributes = True
