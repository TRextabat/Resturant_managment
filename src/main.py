from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.errors import register_all_errors
from src.auth.routers import router as auth_router
from order.routers import router as order_process_router
from src.db.database import AsyncSession
from src.table.seed import seed_tables
from src.table.routers import router as table_router
from src.menu.routers import router as menu_router 
from src.payment.routers import router as payment_router
from src.menu.seed import seed_menus
from fastapi.staticfiles import StaticFiles
from src.user.seeds import seed as user_seed

version = "v1"
version_prefix = f"/api/{version}"

app = FastAPI(
    title="BackEnd",
    description="BackEnd",
    version=version,
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc",
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

register_all_errors(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_router = APIRouter(prefix=version_prefix)

api_router.include_router(auth_router)
api_router.include_router(order_process_router)
app.include_router(api_router)
app.include_router(table_router)
app.include_router(menu_router)
app.include_router(payment_router)

@app.get("/")
def read_root():
    return {"api": "welcome to app "}

@app.on_event("startup")
async def seed_initial_tables():
    async with AsyncSession() as db:
        await seed_tables(db)

@app.on_event("startup")
async def startup():
    async with AsyncSession() as db:
        await seed_menus(db) 


""" @app.on_event("startup")
async def seed_user():
    async with AsyncSession() as db:
        await user_seed()
 
 """
