from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.db.dependencies import get_db
from src.table.schemas import TableCreate, TableResponse, TableUpdate
from src.table.repositories import TableRepository
from src.table.services import TableService

router = APIRouter(prefix="/tables", tags=["Tables"])

@router.post("/", response_model=TableResponse, status_code=status.HTTP_201_CREATED)
async def create_table(
    request: TableCreate,
    db: AsyncSession = Depends(get_db),
):
    service = TableService(TableRepository(db))
    return await service.create_table(request)

@router.get("/", response_model=list[TableResponse])
async def list_tables(
db: AsyncSession = Depends(get_db),
):
    service = TableService(TableRepository(db))
    return await service.get_all_tables()

@router.patch("/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: UUID,
    request: TableUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = TableService(TableRepository(db))
    return await service.update_table(table_id, request)

@router.post("/{table_id}/close", response_model=TableResponse)
async def close_table(
    table_id: UUID,
    db: AsyncSession = Depends(get_db),
    ):
    service = TableService(TableRepository(db))
    return await service.close_table(table_id)