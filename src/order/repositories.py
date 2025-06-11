from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.base_repository import BaseRepository
from sqlalchemy.future import select
from uuid import UUID
from loguru import logger

from src.db.models import Order, OrderItem, OrderStatus
from decimal import Decimal
from typing import List, Optional
from order.schemas import OrderItemCreate


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)

    async def insert(self, order: Order) -> Order:
        logger.info(f"[Repo] Sipariş kaydediliyor | table={order.table_id} | waiter={order.waiter_id}")
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_by_id(self, order_id: UUID) -> Order:
        stmt = select(Order).where(Order.id == order_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


    async def get_orders_for_waiter(self, waiter_id) -> List[Order]:
        stmt = select(Order).where(Order.waiter_id == waiter_id)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
    
    async def get_orders_by_customer(self, customer_id: UUID) -> List[Order]:
        stmt = select(Order).where(Order.customer_id == customer_id)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_orders_for_kitchen(self):
        stmt = select(Order).where(Order.status.in_(["in_progress", "ready"]))
        result = await self.session.execute(stmt)
        orders = result.unique().scalars().all()
        return orders or []

    async def update_status(self, order_id: UUID, new_status: str, is_paid: Optional[bool] = None) -> Order:
        stmt = select(Order).where(Order.id == order_id)
        result = await self.session.execute(stmt)
        order = result.unique().scalar_one_or_none()
        if not order:
            raise Exception("Order not found")

        order.status = new_status
        if is_paid is not None:
            order.is_paid = is_paid

        await self.session.commit()
        await self.session.refresh(order)
        return order
    async def mark_order_as_paid(self, order_id: UUID) -> Order:
        return await self.update_status(order_id, "paid", is_paid=True)