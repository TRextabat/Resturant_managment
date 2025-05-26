from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.errors import register_all_errors
from src.auth.routers import router as auth_router
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
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"api": "welcome to app "}