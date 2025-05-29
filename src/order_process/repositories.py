from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from src.db.models import Order, OrderItem
from decimal import Decimal
from typing import List
from src.order_process.schemas import OrderItemCreate


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, customer_id, table_id, items: List[OrderItemCreate], special_request: str = "") -> Order:
        order = Order(
            id=UUID(),
            customer_id=customer_id,
            table_id=table_id,
            special_request=special_request,
            status="new",
            is_paid=False,
        )

        for item in items:
            order_item = OrderItem(
                menu_item_id=item.menu_item_id,
                item_name=item.item_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
            )
            order.items.append(order_item)

        order.recalc_total()

        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_orders_for_waiter(self, waiter_id) -> List[Order]:
        stmt = select(Order).where(Order.waiter_id == waiter_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_orders_for_kitchen(self):
        stmt = select(Order).where(Order.status.in_(["in_progress", "ready"]))

    async def update_status(self, order_id: UUID, new_status: str) -> Order:
        stmt = select(Order).where(Order.id == order_id)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise Exception("Order not found")
        order.status = new_status
        await self.db.commit()
        await self.db.refresh(order)
        return order
