from sqlalchemy import select
from fastapi import Path
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.user.dependencies import get_db
from src.user.dependencies import get_current_waiter, get_db
from src.user.dependencies import get_current_customer
from src.db.models import User
from fastapi import Query, HTTPException

from src.user.dependencies import get_current_user
from src.db.dependencies import get_db
from order.schemas import (
    CreateOrderRequest,
    OrderResponse,
    OrderStatusUpdateRequest
)
from order.repositories import OrderRepository

from order.services import OrderService
from src.auth.schemas import UserProfileResponse
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    user: UserProfileResponse = Depends(get_current_user)
):
    if not user:
        raise Exception(status= 404)
    service = OrderService(OrderRepository(db))
    return await service.create(customer_id=user.id, request=request)


@router.get("/waiter", response_model=list[OrderResponse])
async def get_orders_for_waiter(
    waiter_id: UUID = Query(..., description="Waiter ID"),
    db: AsyncSession = Depends(get_db)
):
    # waiter_id'nin gerçekten var olup olmadığını kontrol et
    waiter = await db.execute(
        select(User).where(User.id == waiter_id, User.type == "waiter")
    )
    waiter_obj = waiter.scalar_one_or_none()
    if not waiter_obj:
        raise HTTPException(status_code=404, detail="Waiter bulunamadı")

    service = OrderService(OrderRepository(db))
    return await service.get_orders_for_waiter(waiter_id=waiter_id)

@router.patch("/waiter/{order_id}", response_model=OrderResponse)
async def approve_order_by_waiter(
    order_id: UUID,
    waiter_id: UUID = Query(..., description="Waiter ID"),
    db: AsyncSession = Depends(get_db)
):
    # waiter_id geçerliliğini kontrol et
    waiter = await db.execute(
        select(User).where(User.id == waiter_id, User.type == "waiter")
    )
    waiter_obj = waiter.scalar_one_or_none()
    if not waiter_obj:
        raise HTTPException(status_code=404, detail="Waiter bulunamadı")

    service = OrderService(OrderRepository(db))
    return await service.approve_order(order_id=order_id, waiter_id=waiter_id)


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

@router.get("/my", response_model=list[OrderResponse])
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_customer)
):
    service = OrderService(OrderRepository(db))
    return await service.get_orders_for_customer(user.id)

