from http.client import HTTPException
from src.order_process.repositories import OrderRepository
from src.order_process.schemas import CreateOrderRequest, OrderStatusUpdateRequest
from uuid import UUID


class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def create(self, customer_id: UUID, request: CreateOrderRequest):
        return await self.repo.create_order(
            customer_id=customer_id,
            table_id=request.table_id,
            items=request.items,
            special_request=request.special_request
        )

    async def get_orders_for_waiter(self, waiter_id: UUID):
        return await self.repo.get_orders_for_waiter(waiter_id)
    
    async def approve_order(self, order_id: UUID, waiter_id: UUID):
        order = await self.repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
        if order.status != "pending":
            raise HTTPException(status_code=400, detail="Bu sipariş zaten onaylanmış veya geçersiz durumda")
        order.status = "in_progress"  # mutfağa düşer
        order.waiter_id = waiter_id
        await self.db.commit()
        await self.db.refresh(order)
        return order


    async def get_orders_for_kitchen(self):
        return await self.repo.get_orders_for_kitchen()

    async def update_order_status(self, order_id: UUID, new_status: str):
        return await self.repo.update_status(order_id, new_status)
