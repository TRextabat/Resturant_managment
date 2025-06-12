from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional

class MenuCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class MenuCategoryCreate(MenuCategoryBase):
    pass

class MenuCategoryResponse(MenuCategoryBase):
    id: UUID
    class Config:
        from_attributes = True

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category_id: Optional[UUID]
    image_url: Optional[str]

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemResponse(MenuItemBase):
    id: UUID
    class Config:
        from_attributes = True