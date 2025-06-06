tables_data = [
{"table_number": "T1", "capacity": 2},
{"table_number": "T2", "capacity": 4},
{"table_number": "T3", "capacity": 2},
{"table_number": "T4", "capacity": 6},
{"table_number": "T5", "capacity": 3}
]
async def seed_tables(db):
    from src.table.repositories import TableRepository
    from src.table.schemas import TableCreate
    repo = TableRepository(db)
    for t in tables_data:
        if not await repo.get_by_table_number(t["table_number"]):
            await repo.create(TableCreate(**t))