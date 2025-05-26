# src/models/restaurant_table.py
from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.user.models import Customer
from src.db.database import Base
from src.db.models import waiter_table_link

class RestaurantTable(Base):
    """
    One row per physical table in the dining room.

    ── Core columns ────────────────────────────────────────────────────────────
    • `table_number`  – human-visible label (“17”, “B4”, …)
    • `capacity`      – how many seats (≥1)  
    • `location`      – optional zone / section name
    • `is_occupied`   – quick Boolean for fast “free / busy” look-ups
    • `occupied_by`   – FK → customer.id when the table is taken
    • `occupied_at`   – timestamp set when the first guest is seated
    • `created_at`    – row insert timestamp (helps with audits)
    """
    __tablename__ = "restaurant_table"
    __table_args__ = (
        CheckConstraint("capacity >= 1", name="ck_table_capacity_positive"),
    )
    # A human-friendly label, unique in the restaurant
    table_number: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, index=True
    )

    # Seats available (e.g. 2-top, 4-top, 8-top)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    # Optional: section / zone (helps host stand UI)
    location: Mapped[str] = mapped_column(String(32), nullable=True)

    # Occupancy status
    is_occupied: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    occupied_by: Mapped[int] = mapped_column(
        ForeignKey("customer.id", ondelete="SET NULL"), nullable=True
    )
    occupied_at: Mapped[datetime] = mapped_column(nullable=True)


    # ――― Relationships ―――
    customer: Mapped["Customer"] = relationship(
        back_populates="table", lazy="joined"
    )
    waiters: Mapped[list["Waiter"]] = relationship(
        secondary=waiter_table_link, back_populates="tables", lazy="selectin"
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="table", lazy="selectin")

