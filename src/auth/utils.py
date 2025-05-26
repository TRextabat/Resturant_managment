import logging
import uuid
import os
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet, InvalidToken
from src.core.settings import settings
import secrets
from src.core.redis_manager import get_redis
from src.errors import TooManyRequests

# Load encryption key securely
SECRET_KEY = settings.SECRET_KEY
FERNET_KEY = settings.FERNET_KEY
fernet = Fernet(FERNET_KEY.encode())

# Password hashing setup
passwd_context = CryptContext(schemes=[settings.CRYPTO_SCHEME])

ACCESS_TOKEN_EXPIRY = settings.ACCESS_TOKEN_EXP_MIN
REFRESH_TOKEN_EXPIRY = settings.REFRESH_TOKEN_EXPIRY
COOL_DOWN_SECONDS = 60

async def generate_passwd_hash(password: str) -> str:
    """Asynchronously generate a hashed password using Argon2."""
    return passwd_context.hash(password)

async def verify_password(password: str, hashed_password: str) -> bool:
    """Asynchronously verify a password against its hash using Argon2."""
    return passwd_context.verify(password, hashed_password)

async def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    """Create and encrypt a JWT access token."""
    payload = {
        "user": user_data,
        "exp": datetime.now(timezone.utc) + (
            expiry if expiry is not None else timedelta(minutes=ACCESS_TOKEN_EXPIRY if not refresh else REFRESH_TOKEN_EXPIRY)
        ),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return fernet.encrypt(token.encode()).decode()

async def decode_token(token: str) -> dict:
    """Decrypt and decode a JWT token."""
    try:
        decrypted_token = fernet.decrypt(token.encode()).decode()
        return jwt.decode(decrypted_token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logging.error("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        logging.error("Invalid JWT token.")
        return None
    except InvalidToken:
        logging.error("Invalid Fernet-encrypted token.")
        return None

class VerificationCodeManager:
    """Handles storing, retrieving, and deleting verification codes in Redis."""

    @staticmethod
    async def generate_code() -> str:
        """Generate a cryptographically secure 6-digit verification code."""
        return f"{secrets.randbelow(10**6):06d}"

    @classmethod
    async def set_code(cls, email: str, expiry_seconds: int = 300) -> str:
        """Generate and store a verification code in Redis."""
        redis = await get_redis()
        cooldown_key = f"cooldown:{email}"
        if await redis.exists(cooldown_key):
            raise TooManyRequests("Please wait before requesting another code.")

        code = await cls.generate_code()
        await redis.setex(f"verify:{email}", expiry_seconds, code)
        await redis.setex(cooldown_key, COOL_DOWN_SECONDS, "1")
        return code

    @classmethod
    async def get_code(cls, email: str) -> str:
        """Retrieve the stored verification code."""
        redis = await get_redis()
        return await redis.get(f"verify:{email}")

    @classmethod
    async def delete_code(cls, email: str):
        """Remove the verification code after successful verification."""
        redis = await get_redis()
        await redis.delete(f"verify:{email}")