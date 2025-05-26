from sqlalchemy import String, Boolean, DATE, ForeignKey, text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from src.db.database import Base
from src.db.models import waiter_table_link
from uuid import UUID
class User(Base):
    __tablename__ = "user"
    username: Mapped[str] = mapped_column(String, index=True, nullable=True)
    primary_email: Mapped[str] = mapped_column(String, unique=True, index=True)
    primary_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_number: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    type: Mapped[str] = mapped_column(String, nullable=False)  # Discriminator

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": type,
        "with_polymorphic": "*"
    }

class Admin(User):
    __tablename__ = "admin"
    id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), primary_key=True)


    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }


class Waiter(User):
    __tablename__ = "waiter"
    id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    birth_date: Mapped[date] = mapped_column(Date)

    tables: Mapped[list["RestaurantTable"]] = relationship(secondary=waiter_table_link, back_populates="waiters", lazy="selectin")
    orders: Mapped[list["Order"]] = relationship(back_populates="waiter", lazy="selectin")

    __mapper_args__ = {"polymorphic_identity": "waiter"}

class Customer(User):
    __tablename__ = "customer"
    id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)

    table_id: Mapped[UUID] = mapped_column(ForeignKey("restaurant_table.id", ondelete="SET NULL"))

    table: Mapped["RestaurantTable" ] = relationship(back_populates="customer", lazy="selectin")
    orders: Mapped[list["Order"]] = relationship(back_populates="customer", lazy="selectin")

    __mapper_args__ = {"polymorphic_identity": "customer"}

class KitchenStaff(User):
    __tablename__ = "kitchen_staff"
    id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    station: Mapped[str  ] = mapped_column(String(32))
    orders: Mapped[list["Order"]] = relationship(back_populates="waiter", lazy="selectin")
    __mapper_args__ = {"polymorphic_identity": "kitchen_staff"}
