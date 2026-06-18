from pydantic_settings import BaseSettings
from pydantic import computed_field
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Setting(BaseSettings):
    POSTGRES_DB: str
    DB_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    TOKEN_EXP: int = 86400
    ALGORITHM: str = "HS256"
    SECRET_KEY: str
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)
        # If password is empty, don't include the colon after user
        auth = f"{self.POSTGRES_USER}:{encoded_password}" if self.POSTGRES_PASSWORD else self.POSTGRES_USER
        return f"postgresql+asyncpg://{auth}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"


setting = Setting()
