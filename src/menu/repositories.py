from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import MenuItem, MenuCategory
from src.utils.base_repository import BaseRepository

class MenuCategoryRepository(BaseRepository[MenuCategory]):
    def __init__(self, session: AsyncSession):
        super().__init__(MenuCategory, session)

class MenuItemRepository(BaseRepository[MenuItem]):
    def init(self, session: AsyncSession):
        super().init(MenuItem, session)