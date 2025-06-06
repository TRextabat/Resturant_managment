from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base 

# ──────────────────────────────────────────────────────────────────────────────
# Helpers & look‑ups
# ──────────────────────────────────────────────────────────────────────────────

class OrderStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    SERVED = "served"
    PAID = "paid"
    CANCELED = "canceled"

class UserTypes(str, Enum):
    Customer = "custumer"
    waiter = "waiter"
    kitchen = "kitchen"
    admin = "admin"

# Association table for the many‑to‑many between waiters and physical tables
waiter_table_link: Table = Table(
    "waiter_table_link",
    Base.metadata,
    Column("waiter_id", ForeignKey("waiter.id", ondelete="CASCADE"), primary_key=True),
    Column("table_id", ForeignKey("restaurant_table.id", ondelete="CASCADE"), primary_key=True),
)

# ──────────────────────────────────────────────────────────────────────────────
# Base user hierarchy (single‑table inheritance)
# ──────────────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "user"

    username: Mapped[Optional[str]] = mapped_column(String, index=True)
    primary_email: Mapped[str] = mapped_column(String, unique=True, index=True)
    primary_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # single‑table‑inheritance discriminator
    type: Mapped[str] = mapped_column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": type,
        "with_polymorphic": "*",
    }


class Admin(User):
    __tablename__ = "admin"

    id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "admin"}


class Waiter(User):
    __tablename__ = "waiter"

    id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    birth_date: Mapped[date] = mapped_column(Date)

    tables: Mapped[List["RestaurantTable"]] = relationship(
        secondary=waiter_table_link,
        back_populates="waiters",
        lazy="selectin",
    )

    orders: Mapped[List["Order"]] = relationship(
        back_populates="waiter",
        lazy="selectin",
        foreign_keys="[Order.waiter_id]",
    )

    __mapper_args__ = {"polymorphic_identity": "waiter"}


class Customer(User):
    __tablename__ = "customer"

    id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)

    table_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("restaurant_table.id", ondelete="SET NULL"), nullable=True
    )

    table: Mapped[Optional["RestaurantTable"]] = relationship(
        back_populates="customers",
        foreign_keys="[Customer.table_id]",
        lazy="selectin",
    )

    orders: Mapped[List["Order"]] = relationship(
        back_populates="customer",
        lazy="selectin",
        foreign_keys="[Order.customer_id]",
    )

    __mapper_args__ = {"polymorphic_identity": "customer"}


class KitchenStaff(User):
    __tablename__ = "kitchen_staff"

    id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    station: Mapped[str] = mapped_column(String(32))

    orders: Mapped[List["Order"]] = relationship(
        back_populates="kitchen_staff",
        lazy="selectin",
        foreign_keys="[Order.kitchen_staff_id]",
    )

    __mapper_args__ = {"polymorphic_identity": "kitchen_staff"}


# ──────────────────────────────────────────────────────────────────────────────
# Order & line items
# ──────────────────────────────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "order"


    customer_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("customer.id", ondelete="SET NULL"), nullable=True
    )
    waiter_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("waiter.id", ondelete="SET NULL"), nullable=True
    )
    kitchen_staff_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("kitchen_staff.id", ondelete="SET NULL"), nullable=True
    )
    table_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("restaurant_table.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[OrderStatus] = mapped_column(
        SQLAlchemyEnum(OrderStatus, native_enum=False, name="orderstatus"),
        default=OrderStatus.NEW,
        
    )
    special_request: Mapped[Optional[str]] = mapped_column(String(255))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)

    # relationships
    customer: Mapped[Optional["Customer"]] = relationship(
        back_populates="orders",
        lazy="selectin",
        foreign_keys=[customer_id],
    )
    waiter: Mapped[Optional["Waiter"]] = relationship(
        back_populates="orders",
        lazy="selectin",
        foreign_keys=[waiter_id],
    )
    kitchen_staff: Mapped[Optional["KitchenStaff"]] = relationship(
        back_populates="orders",
        lazy="selectin",
        foreign_keys=[kitchen_staff_id],
    )
    table: Mapped[Optional["RestaurantTable"]] = relationship(
        back_populates="orders",
        lazy="selectin",
        foreign_keys=[table_id],
    )

    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined",
        foreign_keys="[OrderItem.order_id]",
    )
    payments: Mapped[List["Payment"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        foreign_keys="[Payment.order_id]",
        lazy="selectin",
    )


    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_order_total_nonnegative"),
    )

    # Helper – keep running total correct
    def recalc_total(self) -> None:
        self.total_amount = sum(item.line_total for item in self.items)


class OrderItem(Base):
    __tablename__ = "order_item"


    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    menu_item_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("menu_item.id", ondelete="SET NULL"), nullable=True
    )

    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped["Order"] = relationship(
        back_populates="items",
        foreign_keys=[order_id],
    )
    menu_item: Mapped[Optional["MenuItem"]] = relationship(
        back_populates="order_items",
        lazy="joined",
        foreign_keys=[menu_item_id],
    )
    
    __table_args__ = (
        CheckConstraint("quantity >= 1", name="ck_item_qty_positive"),
        CheckConstraint("unit_price >= 0", name="ck_item_price_nonnegative"),
    )

    # convenience property
    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity

    



# ──────────────────────────────────────────────────────────────────────────────
# Menu (£ items & categories)
# ──────────────────────────────────────────────────────────────────────────────

class MenuCategory(Base):
    __tablename__ = "menu_category"


    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    items: Mapped[List["MenuItem"]] = relationship(
        back_populates="category",
        lazy="selectin",
        foreign_keys="[MenuItem.category_id]",
    )


class MenuItem(Base):
    __tablename__ = "menu_item"


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
    order_items: Mapped[List["OrderItem"]] = relationship(
        back_populates="menu_item",
        lazy="selectin",
        foreign_keys="[OrderItem.menu_item_id]",
    )

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_menuitem_price_nonnegative"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Physical tables in the dining room
# ──────────────────────────────────────────────────────────────────────────────

class RestaurantTable(Base):
    __tablename__ = "restaurant_table"


    table_number: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    location: Mapped[Optional[str]] = mapped_column(String(32))

    is_occupied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    occupied_by: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("customer.id", ondelete="SET NULL"), nullable=True
    )
    occupied_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # relationships
    customers: Mapped[List["Customer"]] = relationship(
        back_populates="table",
        foreign_keys="[Customer.table_id]",
        lazy="joined",
    )

    # current single occupant (one‑to‑one convenience)
    occupant: Mapped[Optional["Customer"]] = relationship(
        foreign_keys=[occupied_by],
        uselist=False,
        lazy="joined",
        post_update=True,  # helps circular FK updates during seat/leave
    )

    waiters: Mapped[List["Waiter"]] = relationship(
        secondary=waiter_table_link,
        back_populates="tables",
        lazy="selectin",
    )

    orders: Mapped[List["Order"]] = relationship(
        back_populates="table",
        foreign_keys="[Order.table_id]",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("capacity >= 1", name="ck_table_capacity_positive"),
    )

    
# ──────────────────────────────────────────────────────────────────────────────
# Payment
# ──────────────────────────────────────────────────────────────────────────────

class PaymentMethod(str, Enum):
    CARD = "card"
    CASH = "cash"
    POS = "pos"


class Payment(Base):
    __tablename__ = "payment"

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customer.id", ondelete="SET NULL"), nullable=True
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    method: Mapped[PaymentMethod] = mapped_column(
        SQLAlchemyEnum(PaymentMethod, native_enum=False), nullable=False
    )
    is_successful: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # relationships
    order: Mapped["Order"] = relationship(
        back_populates="payments",
        foreign_keys=[order_id],
        lazy="selectin",
    )
    customer: Mapped["Customer"] = relationship(
        foreign_keys=[customer_id],
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payment_amount_positive"),
    )
