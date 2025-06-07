from uuid import UUID
from src.menu.repositories import MenuItemRepository, MenuCategoryRepository
from src.menu.schemas import MenuItemCreate, MenuCategoryCreate

class MenuService:
    def __init__(self, item_repo: MenuItemRepository, category_repo: MenuCategoryRepository):
        self.item_repo = item_repo
        self.category_repo = category_repo
    
    async def create_category(self, data: MenuCategoryCreate):
        return await self.category_repo.create(data)

    async def get_all_categories(self):
        return await self.category_repo.get_all()

    async def create_menu_item(self, data: MenuItemCreate):
        return await self.item_repo.create(data)

    async def get_all_menu_items(self):
        return await self.item_repo.get_all()

    async def get_menu_item_by_id(self, item_id: UUID):
        return await self.item_repo.get_by_id(item_id)
