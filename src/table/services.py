from fastapi import HTTPException
from uuid import UUID
from src.table.schemas import TableCreate, TableUpdate
from src.table.repositories import TableRepository

class TableService:
    def init(self, repo: TableRepository):
        self.repo = repo


    async def create_table(self, request: TableCreate):
        return await self.repo.create(request)

    async def get_all_tables(self):
        return await self.repo.get_all()

    async def update_table(self, table_id: UUID, data: TableUpdate):
        table = await self.repo.get_by_id(table_id)
        if not table:
            raise HTTPException(404, "Masa bulunamadı")
        return await self.repo.update(table_id, data)

    async def close_table(self, table_id: UUID):
        table = await self.repo.get_by_id(table_id)
        if not table:
            raise HTTPException(404, "Masa bulunamadı")
        unpaid_orders = [order for order in table.orders if not order.is_paid]
        if unpaid_orders:
            raise HTTPException(400, "Tüm siparişler ödenmeden masa kapatılamaz")
        update_data = {"is_occupied": False, "occupied_by": None}
        return await self.repo.update(table_id, update_data)