from loguru import logger
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

ACCESS_TOKEN_EXPIRY = 2700
REFRESH_TOKEN_EXPIRY = settings.REFRESH_TOKEN_EXPIRY * 3600*24
COOL_DOWN_SECONDS = 60

async def generate_passwd_hash(password: str) -> str:
    logger.debug("Generating password hash")
    return passwd_context.hash(password)

async def verify_password(password: str, hashed_password: str) -> bool:
    logger.debug("Verifying password against stored hash")
    return passwd_context.verify(password, hashed_password)

async def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    logger.info(f"Creating {'refresh' if refresh else f'access {ACCESS_TOKEN_EXPIRY}'} token for user_id={user_data.get('id')}")
    try:
        payload = {
            "user": user_data,
            "exp": datetime.now(timezone.utc) + (
                expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY if not refresh else REFRESH_TOKEN_EXPIRY)
            ),
            "jti": str(uuid.uuid4()),
            "refresh": refresh,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        logger.debug(f"JWT token successfully created and encrypted {token}")
        return fernet.encrypt(token.encode()).decode()
    except Exception:
        logger.error(f"faild to create token {Exception}")

async def decode_token(token: str) -> dict:
    logger.debug("Attempting to decrypt and decode token")
    try:
        decrypted_token = fernet.decrypt(token.encode()).decode()
        decoded = jwt.decode(decrypted_token, SECRET_KEY, algorithms=["HS256"])
        logger.debug(f"Token decoded successfully: jti={decoded.get('jti')}, user_id={decoded['user'].get('id')}")
        return decoded
    except jwt.ExpiredSignatureError as e:
        logger.warning(f"Token has expired {e}")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token structure{e}")
        return None
    except InvalidToken as e:
        logger.warning(f"Fernet decryption failed — Invalid token{e}")
        return None

class VerificationCodeManager:
    """Handles storing, retrieving, and deleting verification codes in Redis."""

    @staticmethod
    async def generate_code() -> str:
        code = f"{secrets.randbelow(10**6):06d}"
        logger.debug(f"Generated verification code: {code}")
        return code

    @classmethod
    async def set_code(cls, email: str, expiry_seconds: int = 300) -> str:
        redis = await get_redis()
        cooldown_key = f"cooldown:{email}"
        logger.debug(f"Checking cooldown for email: {email}")
        if await redis.exists(cooldown_key):
            logger.warning(f"Too many requests for email: {email}")
            raise TooManyRequests("Please wait before requesting another code.")

        code = await cls.generate_code()
        await redis.setex(f"verify:{email}", expiry_seconds, code)
        await redis.setex(cooldown_key, COOL_DOWN_SECONDS, "1")
        logger.info(f"Verification code set for {email}")
        return code

    @classmethod
    async def get_code(cls, email: str) -> str:
        redis = await get_redis()
        code = await redis.get(f"verify:{email}")
        logger.debug(f"Retrieved verification code for {email}: {code}")
        return code

    @classmethod
    async def delete_code(cls, email: str):
        redis = await get_redis()
        await redis.delete(f"verify:{email}")
        logger.info(f"Deleted verification code for {email}")
