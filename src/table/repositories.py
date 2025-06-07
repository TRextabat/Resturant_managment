from sqlalchemy import select
from typing import Optional
from src.db.models import RestaurantTable
from src.utils.base_repository import BaseRepository

class TableRepository(BaseRepository[RestaurantTable]):
    def __init__(self, session):
       super().__init__(RestaurantTable, session)

    async def get_by_table_number(self, table_number: str) -> Optional[RestaurantTable]:
        stmt = select(RestaurantTable).where(RestaurantTable.table_number == table_number)
        result = await self.session.execute(stmt)
        return result.unique().scalars().first()