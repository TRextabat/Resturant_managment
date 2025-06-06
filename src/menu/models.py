from uuid import UUID
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.database import Base

class MenuCategory(Base):
    tablename = "menu_category"
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    items: Mapped[List["MenuItem"]] = relationship(
        back_populates="category",
        lazy="selectin",
        foreign_keys="[MenuItem.category_id]",
    )

class MenuItem(Base):
    tablename = "menu_item"
    category_id: Mapped[Optional[UUID]] = mapped_column(
    ForeignKey("menu_category.id", ondelete="SET NULL"), index=True, nullable=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    category: Mapped[Optional["MenuCategory"]] = relationship(
        back_populates="items",
        lazy="joined",
        foreign_keys=[category_id],
    )

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_menuitem_price_nonnegative"),
    )

    
