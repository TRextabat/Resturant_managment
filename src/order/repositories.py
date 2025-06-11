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

    async def create_order(self, customer_id, waiter_id, table_id, items: List[OrderItemCreate], special_request: str = "") -> Order:
        logger.info(f"[Repo] Yeni sipariş ekleniyor | customer={customer_id} | table={table_id}")
        try:
            order = Order(
                customer_id=customer_id,
                waiter_id=waiter_id,
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

            self.session.add(order)
            await self.session.commit()
            await self.session.refresh(order)
            logger.info(f"[Repo] Sipariş başarıyla eklendi | order_id={order.id}")
            return order
        except Exception as e:
            logger.exception(f"[Repo] Sipariş veritabanına yazılamadı | Hata: {e}")
            raise

    async def get_orders_for_waiter(self, waiter_id) -> List[Order]:
        stmt = select(Order).where(Order.waiter_id == waiter_id)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
    
    async def get_orders_by_customer(self, customer_id: UUID) -> List[Order]:
        stmt = select(Order).where(Order.customer_id == customer_id)
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

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