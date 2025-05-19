import redis.asyncio as redis
from src.core.settings import settings

class RedisManager:
    """
    Manages a shared async Redis client instance for caching.
    """

    _client = None  # Singleton Redis client

    @classmethod
    async def get_client(cls, redis_db: int = settings.REDIS_DB) -> redis.Redis:
        """
        Returns a shared async Redis client instance.

        Returns:
            redis.Redis: An async Redis client instance.
        """
        if cls._client is None:
            try:
                cls._client = await redis.from_url(
                    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{redis_db}",
                    decode_responses=True,
                    socket_timeout=5,  # Prevents hanging connections
                    health_check_interval=30  # Ensures periodic connection checks
                )

                # Test connection immediately
                await cls._client.ping()
                await cls._client.set("test_key", "test_value")  # Test write operation
                await cls._client.get("test_key")  # Test read operation
            except Exception as e:
                raise RuntimeError(f"Failed to connect to Redis: {e}")

        return cls._client

    @classmethod
    async def close_client(cls):
        """
        Closes the Redis client connection if it exists.
        """
        if cls._client:
            await cls._client.close()
            cls._client = None

async def get_redis() -> redis.Redis:
    """
    Dependency function to get the Redis client instance.

    Returns:
        redis.Redis: The Redis client instance.
    """
    return await RedisManager.get_client()


class TokenBlocklist:
    """
    Manages token blacklisting using Redis.
    """

    @staticmethod
    async def add_token_to_blocklist(jti: str, expiry_seconds: int = settings.TOKEN_BLOCK_LIST_EXPIRY):
        """
        Adds a JWT token to the blocklist using JTI with an expiry time.
        """
        client = await RedisManager.get_client()
        await client.setex(name=jti, value="", ex=expiry_seconds)

    @staticmethod
    async def is_token_blacklisted(jti: str) -> bool:
        """
        Checks if a JWT token is blacklisted using JTI.
        """
        client = await RedisManager.get_client()
        return await client.exists(jti) > 0