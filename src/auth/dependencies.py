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
from loguru import logger 

class TokenBearer(HTTPBearer):
    """Base class for handling authentication token verification."""

    token_type: str = None  # To be defined by subclasses ("access" or "refresh")

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)
        self.token_blocklist = TokenBlocklist()

    async def __call__(self, request: Request, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> dict:
        """Extract token from request & validate it."""
        token = credentials.credentials
        logger.debug(f"Received token: {token[:10]}...")  # Avoid logging full tokens in production

        token_data = await decode_token(token)
        logger.debug(f"Decoded token data: {token_data}")

        if not token_data or "jti" not in token_data:
            logger.warning("Token decoding failed or missing 'jti'")
            raise InvalidToken()

        if await self.token_blocklist.is_token_blacklisted(token_data["jti"]):
            logger.warning(f"Token with jti={token_data['jti']} is blacklisted")
            raise InvalidToken()

        await self.verify_token_type(token_data)

        logger.info(f"Token verified successfully for user_id={token_data.get('user', {}).get('id')}")
        return token_data

    async def verify_token_type(self, token_data: dict):
        if self.token_type is None:
            raise NotImplementedError("Token type must be defined in subclasses.")

        is_refresh_token = token_data.get("refresh", False)
        logger.debug(f"Verifying token type: expected={self.token_type}, actual={'refresh' if is_refresh_token else 'access'}")

        if self.token_type == "access" and is_refresh_token:
            logger.warning("Refresh token used where access token expected")
            raise AccessTokenRequired()

        if self.token_type == "refresh" and not is_refresh_token:
            logger.warning("Access token used where refresh token expected")
            raise RefreshTokenRequired()


class AccessTokenBearer(TokenBearer):
    token_type = "access"


class RefreshTokenBearer(TokenBearer):
    token_type = "refresh"


async def get_current_user(
    token_data: dict = Depends(AccessTokenBearer()),
    db: AsyncSession = Depends(get_db)
):
    """Extracts and validates the current user from the access token."""
    logger.info(f"Fetching user with ID: {token_data['user']['id']}")
    user_repo = UserRepository(db)

    user = await user_repo.get_by_id(token_data["user"]["id"])
    if not user:
        logger.error(f"User not found for ID: {token_data['user']['id']}")
        raise UserNotFound()

    logger.info(f"User found: {user.primary_email}")
    return UserProfileResponse.model_validate(user)
