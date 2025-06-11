from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from src.db.database import Base
from src.db.models import Payment  
from src.utils.base_repository import BaseRepository  


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession):
        super().__init__(Payment, session)

    async def get_payments_by_order(self, order_id: UUID) -> List[Payment]:
        stmt = select(Payment).where(Payment.order_id == order_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_payments_by_customer(self, customer_id: UUID) -> List[Payment]:
        stmt = select(Payment).where(Payment.customer_id == customer_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_total_payments_for_order(self, order_id: UUID) -> Decimal:
        stmt = select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.order_id == order_id, Payment.is_successful == True
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_successful_payments(self) -> List[Payment]:
        stmt = select(Payment).where(Payment.is_successful == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_payments_in_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Payment]:
        stmt = select(Payment).where(
            Payment.paid_at >= start_date,
            Payment.paid_at <= end_date,
            Payment.is_successful == True
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
