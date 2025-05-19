from sqlalchemy import create_engine
from sqlalchemy import  Boolean, UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import  as_declarative, declared_attr, Mapped, mapped_column
from src.core.settings import settings
from datetime import datetime
import uuid

DATABASE_URL = f'postgresql+asyncpg://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}'

async_engine = create_async_engine(DATABASE_URL)
AsyncSession = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)

@as_declarative()
class Base():
    __allow_unmapped__ = True  # Allow unmapped attributes



    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, 
        nullable=False, index=True, 
        server_default=text("gen_random_uuid()")
    )
   
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
# Create tables
#Base.metadata.create_all(bind=engine)