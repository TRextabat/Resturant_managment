from sqlalchemy import String, Boolean, DATE, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from src.db.database import Base

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[str] = mapped_column(server_default=text("CURRENT_TIMESTAMP"))

    username: Mapped[str] = mapped_column(String, index=True, nullable=True)
    primary_email: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    primary_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_number: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    type: Mapped[str] = mapped_column(String, nullable=False)  # Discriminator

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": type,
        "with_polymorphic": "*"
    }

class Admin(User):
    __tablename__ = "admin"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)


    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }


class Waiter(User):
    __tablename__ = "waiter"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    birth_date: Mapped[date | None] = mapped_column(DATE, nullable=True)
    assigned_tables: Mapped[int | None] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "waiter",
    }

class Customer(User):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    table_number: Mapped[int | None] = mapped_column(nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "customer",
    }

class KitchenStaff(User):
    __tablename__ = "kitchen_staff"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)

    station: Mapped[str | None] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "kitchen_staff",
    }
