from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from enum import Enum


class OrderStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    SERVED = "served"
    PAID = "paid"
    CANCELED = "canceled"


class OrderItemCreate(BaseModel):
    menu_item_id:UUID
    item_name: str
    unit_price: Decimal
    quantity: int = Field(..., gt=0)


class CreateOrderRequest(BaseModel):
    table_id: UUID
    special_request: Optional[str] = ""
    items: List[OrderItemCreate]


class OrderItemResponse(OrderItemCreate):
    line_total: Decimal


class OrderResponse(BaseModel):
    id: UUID
    table_id: UUID
    waiter_id: Optional[UUID]
    status: OrderStatus
    special_request: Optional[str]
    total_amount: Decimal
    is_paid: bool
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderStatusUpdateRequest(BaseModel):
    new_status: OrderStatus
