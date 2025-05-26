from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependencies import get_db
from src.auth.services import AuthService
from src.auth.schemas import (
    TokenResponse, 
    TokenRefreshRequest, 
    UserProfileResponse,
    RegisterRequest,
    VerifyEmailResponse,
    VerifyEmailRequest,
)
from src.auth.dependencies import AccessTokenBearer, RefreshTokenBearer, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])



@router.post("/register")
async def register_user(request: RegisterRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    return await AuthService.register_user(request, background_tasks, db)

@router.post("/verify", response_model=VerifyEmailResponse)
async def verify_email(request: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.verify_email(request, db)

@router.post("/login", response_model=TokenResponse)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.login_user(form_data.username, form_data.password, db)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
):
    return await AuthService.refresh_token(request)

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user(
    current_user: UserProfileResponse = Depends(get_current_user),  
):
    return current_user

@router.post("/logout")
async def logout(
    token_data: dict = Depends(RefreshTokenBearer()),  #  Ensures only refresh tokens are used
    db: AsyncSession = Depends(get_db)
):
    """Logs out the user by revoking the refresh token."""
    return await AuthService.logout_user(token_data, db)