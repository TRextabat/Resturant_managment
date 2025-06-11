from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from datetime import datetime

from src.payment.schemas import PaymentCreate, PaymentUpdate, PaymentRead
from src.payment.services import PaymentService
from src.db.dependencies import get_db
from src.auth.dependencies import get_current_user
from src.auth.schemas import UserProfileResponse
router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


def get_payment_service(session: AsyncSession = Depends(get_db)) -> PaymentService:
    return PaymentService(session)


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_in: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
    user: UserProfileResponse = Depends(get_current_user)  
):
    payment = await service.create_payment(payment_in)
    return payment


@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment_by_id(
    payment_id: UUID,
    service: PaymentService = Depends(get_payment_service),
    user: UserProfileResponse = Depends(get_current_user)  

):
    payment = await service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.patch("/{payment_id}", response_model=PaymentRead)
async def update_payment(
    payment_id: UUID,
    payment_in: PaymentUpdate,
    service: PaymentService = Depends(get_payment_service),
    user: UserProfileResponse = Depends(get_current_user)
):
    payment = await service.update_payment(payment_id, payment_in)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: UUID,
    service: PaymentService = Depends(get_payment_service),
    user: UserProfileResponse = Depends(get_current_user)
):
    deleted = await service.delete_payment(payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return None


@router.get("/order/{order_id}", response_model=List[PaymentRead])
async def get_payments_by_order(
    order_id: UUID,
    service: PaymentService = Depends(get_payment_service),
    user: UserProfileResponse = Depends(get_current_user)
):
    return await service.get_payments_by_order(order_id)


@router.get("/customer/{customer_id}", response_model=List[PaymentRead])
async def get_payments_by_customer(
    customer_id: UUID,
    service: PaymentService = Depends(get_payment_service),
    user: UserProfileResponse = Depends(get_current_user)
):
    return await service.get_payments_by_customer(customer_id)


@router.get("/order/{order_id}/total", response_model=float)
async def get_total_paid_for_order(
    order_id: UUID,
    service: PaymentService = Depends(get_payment_service),
    user: UserProfileResponse = Depends(get_current_user)
):
    total = await service.get_total_paid_for_order(order_id)
    return float(total) 


@router.get("/successful", response_model=List[PaymentRead])
async def get_successful_payments(
    service: PaymentService = Depends(get_payment_service),
    user: UserProfileResponse = Depends(get_current_user)
):
    return await service.get_successful_payments()


@router.get("/range", response_model=List[PaymentRead])
async def get_payments_in_date_range(
    start_date: datetime,
    end_date: datetime,
    service: PaymentService = Depends(get_payment_service),
    user: UserProfileResponse = Depends(get_current_user)
):
    return await service.get_payments_in_date_range(start_date, end_date)
