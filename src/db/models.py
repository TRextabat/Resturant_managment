from sqlalchemy import ForeignKey, String, Date, Boolean, Integer, Table, Column
from sqlalchemy.orm import Mapped, relationship
from src.db.database import Base

waiter_table_link: Table = Table(
    "waiter_table_link",
    Base.metadata,
    Column("waiter_id", ForeignKey("waiter.id", ondelete="CASCADE"), primary_key=True),
    Column("table_id", ForeignKey("restaurant_table.id", ondelete="CASCADE"), primary_key=True),
)