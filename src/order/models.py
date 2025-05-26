from __future__ import annotations
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional
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
from src.order.enums import OrderStatus
from src.user.models import Customer, Waiter
from src.db.database import Base
from src.db.models import waiter_table_link


class Order(Base):
    __tablename__ = "order"
    __table_args__ = (CheckConstraint("total_amount >= 0"),)
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customer.id", ondelete="SET NULL")
    )
    waiter_id: Mapped[UUID] = mapped_column(
        ForeignKey("waiter.id", ondelete="SET NULL")
    )
    kitchen_staff_id: Mapped[UUID] = mapped_column(
        ForeignKey("kitchen_staff.id", ondelete="SET NULL")
        )

    table_id: Mapped[UUID] = mapped_column(
        ForeignKey("restaurant_table.id", ondelete="SET NULL")
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False), default=OrderStatus.NEW
    )
    special_request: Mapped[str] = mapped_column(String(255))

    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)

    # ─── Relationships ──────────────────────────────────────────────
    customer:       Mapped["Customer"]        = relationship(back_populates="orders", lazy="selectin")
    waiter:         Mapped["Waiter"]          = relationship(back_populates="orders", lazy="selectin")
    kitchen_staff:  Mapped["KitchenStaff"]    = relationship(back_populates="orders", lazy="selectin")
    table:          Mapped["RestaurantTable"] = relationship(back_populates="orders", lazy="selectin")

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="joined"
    )

    # optional helper to keep totals consistent
    def recalc_total(self) -> None:
        self.total_amount = sum(item.line_total for item in self.items)


class OrderItem(Base):
    __tablename__ = "order_item"
    __table_args__ = (
        CheckConstraint("quantity >= 1"),
        CheckConstraint("unit_price >= 0"),
    )

    order_id:     Mapped[UUID]          = mapped_column(
        ForeignKey("order.id", ondelete="CASCADE")
    )
    menu_item_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("menu_item.id", ondelete="SET NULL")
    )

    item_name:  Mapped[str]     = mapped_column(String(100), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity:   Mapped[int]     = mapped_column(Integer, default=1)


    # relationships
    order:     Mapped["Order"]     = relationship(back_populates="items")
    menu_item: Mapped["MenuItem"]  = relationship(
        back_populates="order_items", lazy="joined"
    )

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity