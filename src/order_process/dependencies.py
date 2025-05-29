from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dependencies import get_db
from src.user.repositories import UserRepository
from src.db.models import User
from src.auth.dependencies import get_current_user
from src.auth.schemas import UserProfileResponse

async def get_order_db() -> AsyncSession:
    """Order modülü için veritabanı oturumu sağlar."""
    return await get_db()


async def get_order_current_user(
    user: UserProfileResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Giriş yapmış kullanıcıyı döner — müşteri mi kontrol edebilirsin."""

    repo = UserRepository(db)
    full_user = await repo.get_by_id(user.id)
    if not full_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return full_user


async def get_current_customer(
    user: User = Depends(get_order_current_user)
) -> User:
    """Sadece müşteri rolünde kullanıcıya izin verir."""
    if user.type != "customer":
        raise HTTPException(status_code=403, detail="Only customers can perform this action.")
    return user


async def get_current_waiter(
    user: User = Depends(get_order_current_user)
) -> User:
    """Sadece garson rolünde kullanıcıya izin verir."""
    if user.type != "waiter":
        raise HTTPException(status_code=403, detail="Only waiters can access this endpoint.")
    return user


async def get_current_kitchen_staff(
    user: User = Depends(get_order_current_user)
) -> User:
    """Sadece mutfak personeli erişebilir."""
    if user.type != "kitchen_staff":
        raise HTTPException(status_code=403, detail="Only kitchen staff can access this.")
    return user
