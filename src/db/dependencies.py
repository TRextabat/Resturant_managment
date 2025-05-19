from sqlalchemy.orm import Session
from db.database import AsyncSession

async def get_db():
    """Dependency for FastAPI routes to use the database session."""
    async with AsyncSession() as session:
        yield session