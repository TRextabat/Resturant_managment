from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.order_process.dependencies import get_db
from src.order_process.dependencies import get_current_waiter, get_db

from src.order_process.dependencies import get_current_user
from src.db.dependencies import get_db
from src.order_process.schemas import (
    CreateOrderRequest,
    OrderResponse,
    OrderStatusUpdateRequest
)
from src.order_process.repositories import OrderRepository
from src.order_process.services import OrderService
from src.auth.schemas import UserProfileResponse
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    user: UserProfileResponse = Depends(get_current_user)
):
    if not get_current_user:
        raise Exception(status= 404)
    service = OrderService(OrderRepository(db))
    return await service.create(customer_id=user.id, request=request)


@router.get("/waiter", response_model=list[OrderResponse])
async def get_orders_for_waiter(
    db: AsyncSession = Depends(get_db),
    user: UserProfileResponse = Depends(get_current_user)
):
    service = OrderService(OrderRepository(db))
    return await service.get_orders_for_waiter(waiter_id=user.id)

@router.post("/orders/{order_id}/approve", response_model=OrderResponse)
async def approve_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    waiter = Depends(get_current_waiter)
):
    service = OrderService(db)
    return await service.approve_order(order_id, waiter.id)


@router.get("/kitchen", response_model=list[OrderResponse])
async def get_orders_for_kitchen(
    db: AsyncSession = Depends(get_db),
    _user: UserProfileResponse = Depends(get_current_user)
):
    service = OrderService(OrderRepository(db))
    return await service.get_orders_for_kitchen()


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _user: UserProfileResponse = Depends(get_current_user)
):
    service = OrderService(OrderRepository(db))
    return await service.update_order_status(order_id=order_id, new_status=payload.new_status)
