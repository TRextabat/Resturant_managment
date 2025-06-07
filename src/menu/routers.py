from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependencies import get_db
from src.menu.schemas import (
MenuItemCreate,
MenuItemResponse,
MenuCategoryCreate,
MenuCategoryResponse
)
from src.menu.repositories import MenuItemRepository, MenuCategoryRepository
from src.menu.services import MenuService

router = APIRouter(prefix="/menu", tags=["Menu"])

def get_service(db: AsyncSession = Depends(get_db)):
    item_repo = MenuItemRepository(db)
    category_repo = MenuCategoryRepository(db)
    return MenuService(item_repo, category_repo)

@router.post("/categories", response_model=MenuCategoryResponse)
async def create_category(request: MenuCategoryCreate, service: MenuService = Depends(get_service)):
    return await service.create_category(request)

@router.get("/categories", response_model=list[MenuCategoryResponse])
async def list_categories(service: MenuService = Depends(get_service)):
    return await service.get_all_categories()

@router.post("/items", response_model=MenuItemResponse)
async def create_item(request: MenuItemCreate, service: MenuService = Depends(get_service)):
    return await service.create_menu_item(request)

@router.get("/items", response_model=list[MenuItemResponse])
async def list_items(service: MenuService = Depends(get_service)):
    return await service.get_all_menu_items()