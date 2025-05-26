from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    text,
)
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.order.models import OrderItem
from src.db.database import Base

class MenuCategory(Base):
    __tablename__ = "menu_category"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str ] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    items: Mapped[list["MenuItem"]] = relationship(back_populates="category", lazy="selectin")

class MenuItem(Base):
    __tablename__ = "menu_item"
    __table_args__ = (CheckConstraint("price >= 0"),)

    category_id: Mapped[UUID ] = mapped_column(ForeignKey("menu_category.id", ondelete="SET NULL"), index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str ] = mapped_column(String(255))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped["MenuCategory" ] = relationship(back_populates="items", lazy="joined")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="menu_item", lazy="selectin")
