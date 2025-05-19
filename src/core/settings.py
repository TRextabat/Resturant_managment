from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_USERNAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXP_MIN: int
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str
    JWT_SIGN_ALGORITHM: str
    JWT_ENCRYPTION_ALGORITHM: str
    CRYPTO_SCHEME: str
    REFRESH_TOKEN_EXPIRY: int
    MAIL_FROM: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    FERNET_KEY: str
    TOKEN_BLOCK_LIST_EXPIRY: int

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()