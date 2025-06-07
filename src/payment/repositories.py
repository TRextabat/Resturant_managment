from src.utils.base_repository import BaseRepository
from src.models import Payment
from sqlalchemy.future import select
from sqlalchemy import func
from uuid import UUID
from typing import List, Optional


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session):
        super().__init__(Payment, session)

    async def get_by_order_id(self, order_id: UUID) -> List[Payment]:
        stmt = select(Payment).where(Payment.order_id == order_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_total_paid_for_order(self, order_id: UUID) -> float:
        stmt = select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.order_id == order_id,
            Payment.is_successful == True
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
