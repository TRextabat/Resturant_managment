from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.db.dependencies import get_db
from src.auth.utils import decode_token
from src.errors import InvalidToken, RefreshTokenRequired, AccessTokenRequired
from src.core.redis_manager import TokenBlocklist
from src.user.repositories import UserRepository
from src.errors import UserNotFound
from src.auth.schemas import UserProfileResponse
class TokenBearer(HTTPBearer):
    """Base class for handling authentication token verification."""

    token_type: str = None  # To be defined by subclasses ("access" or "refresh")

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)
        self.token_blocklist = TokenBlocklist()
        

    async def __call__(self, request: Request, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> dict:
        """Extract token from request & validate it."""
        token = credentials.credentials  # Extract manually 

        token_data = await decode_token(token)
        if not token_data or "jti" not in token_data:
            raise InvalidToken()

        if await self.token_blocklist.is_token_blacklisted(token_data["jti"]):
            raise InvalidToken()

        # Validate if it's an access or refresh token
        await self.verify_token_type(token_data)

        return token_data

    async def verify_token_type(self, token_data: dict):
        """To be implemented by subclasses for access or refresh token verification."""
        if self.token_type is None:
            raise NotImplementedError("Token type must be defined in subclasses.")

        is_refresh_token = token_data.get("refresh", False)

        if self.token_type == "access" and is_refresh_token:
            raise AccessTokenRequired()

        if self.token_type == "refresh" and not is_refresh_token:
            raise RefreshTokenRequired()


class AccessTokenBearer(TokenBearer):
    """Ensures the provided token is an **access token** (not refresh)."""
    
    token_type = "access"  # Set the token type


class RefreshTokenBearer(TokenBearer):
    """Ensures the provided token is a **refresh token** (not access)."""

    token_type = "refresh"  # Set the token type


async def get_current_user(
    token_data: dict = Depends(AccessTokenBearer()),  #Secure token validation
    db: AsyncSession = Depends(get_db)
):
    """Extracts and validates the current user from the access token."""
    user_repo = UserRepository(db)
    
    user = await user_repo.get_by_id(token_data["user"]["id"])
    if not user:
        raise UserNotFound()

    return UserProfileResponse.model_validate(user)