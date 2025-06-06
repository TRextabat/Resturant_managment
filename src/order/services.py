
from fastapi import HTTPException
from order.repositories import OrderRepository
from order.schemas import CreateOrderRequest, OrderStatusUpdateRequest
from uuid import UUID
from loguru import logger
import random
from src.db.models import User
from sqlalchemy import select, func
from src.order.enums import OrderStatus


class OrderService:
    def __init__(self, db: OrderRepository):
        self.db = db

    async def create(self, customer_id: UUID, request: CreateOrderRequest):
         # Rastgele waiter seç
        stmt = select(User).where(User.type == "waiter")
        result = await self.db.session.execute(stmt)
        waiters = result.scalars().all()


        if not waiters:
            raise HTTPException(status_code=404, detail="Hiç garson bulunamadı")

        random_waiter = random.choice(waiters)

        try:
            logger.info(f" Sipariş oluşturuluyor | customer_id={customer_id} | table_id={request.table_id}")
            return await self.db.create_order(
            customer_id=customer_id,
            waiter_id=random_waiter.id,
            table_id=request.table_id,
            items=request.items,
            special_request=request.special_request,
        
        )
    
        except Exception as e:
            logger.exception(f"💥 Sipariş oluşturulamadı | Hata: {e}")
            raise HTTPException(status_code=500, detail="Sipariş oluşturulamadı")
        
    

    async def get_orders_for_waiter(self, waiter_id: UUID,):
        return await self.db.get_orders_for_waiter(waiter_id)
        
    
    async def get_orders_for_customer(self, customer_id: UUID):
        """Müşterinin kendi verdiği siparişleri getirir."""
        return await self.db.get_orders_by_customer(customer_id)
    
    async def approve_order(self, order_id: UUID, waiter_id: UUID):
        order = await self.db.get_by_id(order_id)
        order.status = OrderStatus.READY
        logger.info(f"Sipariş durumu: {order.status}")

        if not order:
            raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
        if order.status != "ready":
            raise HTTPException(status_code=400, detail="Bu sipariş zaten onaylanmış veya geçersiz durumda")
        order.status = OrderStatus.IN_PROGRESS  # mutfağa düşer
        order.waiter_id = waiter_id
        await self.db.session.commit()
        await self.db.session.refresh(order)
        return order


    async def get_orders_for_kitchen(self):
        orders = await self.db.get_orders_for_kitchen()
        return orders or []

    async def update_order_status(self, order_id: UUID, new_status: str):
        order = await self.db.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        order.status = new_status
        await self.db.session.commit()
        await self.db.session.refresh(order)
        return order
