from datetime import date
import uuid
from passlib.context import CryptContext

from src.db.models import Waiter, RestaurantTable, KitchenStaff
from src.core.settings import settings
from src.db.database import AsyncSession
from loguru import logger


passwd_context = CryptContext(schemes=[settings.CRYPTO_SCHEME])


async def generate_passwd_hash(password: str) -> str:
    logger.debug("Generating password hash")
    return passwd_context.hash(password)


async def seed():
    logger.debug("Seeding initial data")

    async with AsyncSession() as session:
        # Generate passwords
        waiter1_hash = await generate_passwd_hash("john123")
        waiter2_hash = await generate_passwd_hash("jane456")
        chef_hash = await generate_passwd_hash("chef789")

        # Create waiters
        waiter1 = Waiter(
            id=uuid.uuid4(),
            username="waiter_john",
            primary_email="john1@example.com",
            primary_email_verified=True,
            hashed_password=waiter1_hash,
            birth_date=date(1990, 1, 1),
            type="waiter"
        )

        # Create kitchen staff
        kitchen_staff = KitchenStaff(
            id=uuid.uuid4(),
            username="chef_mike",
            primary_email="mike1@example.com",
            primary_email_verified=True,
            hashed_password=chef_hash,
            station="Grill",
            type="kitchen"
        )


        # Add everything to DB
        session.add_all([waiter1])
        await session.commit()

        logger.info("✅ Seeding completed successfully.")
