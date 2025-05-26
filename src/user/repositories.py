from src.utils.base_repository import BaseRepository
from src.db.models import(
    User,
    Admin,
    Waiter,
    Customer,
    KitchenStaff
)
from sqlalchemy.future import select
from typing import Optional, Type
class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(User, session)
    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    #TODO handle secondary email
    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.primary_email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()
class AdminRepository(BaseRepository[Admin]):
    def __init__(self, session):
        super().__init__(Admin, session)

    

class WaiterRepository(BaseRepository[Waiter]):
    def __init__(self, session):
        super().__init__(Waiter, session)

    async def increment_tables_served(self, waiter_id: int):
        return await self.increment_field(waiter_id, "total_tables_served")

    async def increment_orders_taken(self, waiter_id: int):
        return await self.increment_field(waiter_id, "total_orders_taken")
    

class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session):
        super().__init__(Customer, session)

    async def increment_visits(self, customer_id: int):
        return await self.increment_field(customer_id, "total_visits")

    async def increment_spent(self, customer_id: int, amount: int):
        return await self.increment_field(customer_id, "total_amount_spent", step=amount)
    


class KitchenStaffRepository(BaseRepository[KitchenStaff]):
    def __init__(self, session):
        super().__init__(KitchenStaff, session)

    async def increment_orders_prepared(self, staff_id: int):
        return await self.increment_field(staff_id, "total_orders_prepared")


