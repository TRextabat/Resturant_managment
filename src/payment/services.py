from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.payment.repositories import PaymentRepository
from src.order.repositories import OrderRepository
from src.payment.schemas import PaymentCreate, PaymentUpdate
from src.db.models import Payment


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payment_repo = PaymentRepository(session)
        self.order_repo = OrderRepository(session)

    async def create_payment(self, data: PaymentCreate) -> Payment:
        payment = await self.payment_repo.create(data)

        if data.is_successful:
            await self.order_repo.mark_order_as_paid(data.order_id)

        return payment

    async def update_payment(self, payment_id: UUID, data: PaymentUpdate) -> Optional[Payment]:
        payment = await self.payment_repo.update(payment_id, data)

        # Check if payment became successful after update
        if data.is_successful:
            await self.order_repo.mark_order_as_paid(payment.order_id)

        return payment

    async def get_payment_by_id(self, payment_id: UUID) -> Optional[Payment]:
        return await self.payment_repo.get_by_id(payment_id)

    async def delete_payment(self, payment_id: UUID) -> bool:
        return await self.payment_repo.delete(payment_id)

    async def get_payments_by_order(self, order_id: UUID) -> List[Payment]:
        return await self.payment_repo.get_payments_by_order(order_id)

    async def get_payments_by_customer(self, customer_id: UUID) -> List[Payment]:
        return await self.payment_repo.get_payments_by_customer(customer_id)

    async def get_total_paid_for_order(self, order_id: UUID) -> Decimal:
        return await self.payment_repo.get_total_payments_for_order(order_id)

    async def get_successful_payments(self) -> List[Payment]:
        return await self.payment_repo.get_successful_payments()

    async def get_payments_in_date_range(self, start_date: datetime, end_date: datetime) -> List[Payment]:
        return await self.payment_repo.get_payments_in_date_range(start_date, end_date)
