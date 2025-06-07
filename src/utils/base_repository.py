from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from typing import Type, TypeVar, Generic, List, Optional, Union
from src.db.database import Base
from pydantic import BaseModel

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, obj_in: Union[BaseModel, dict]) -> T:
        obj_data = obj_in.model_dump() if isinstance(obj_in, BaseModel) else obj_in
        obj = self.model(**obj_data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, obj_id: str) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(stmt)
        return result.unique().scalars().first()

    async def get_all(self) -> List[T]:
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def update(self, obj_id: str, update_data: Union[BaseModel, dict]) -> Optional[T]:
        obj = await self.get_by_id(obj_id)
        if not obj:
            return None
        update_dict = update_data.model_dump(exclude_unset=True) if isinstance(update_data, BaseModel) else update_data
        for key, value in update_dict.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj_id: str) -> bool:
        obj = await self.get_by_id(obj_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.commit()
        return True

    async def increment_field(self, obj_id: Union[str, int], field_name: str, step: int = 1) -> Optional[T]:
        obj = await self.get_by_id(obj_id)
        if not obj:
            return None
        if hasattr(obj, field_name):
            current_value = getattr(obj, field_name, 0)
            setattr(obj, field_name, current_value + step)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        raise AttributeError(f"{self.model.__name__} has no field '{field_name}'")