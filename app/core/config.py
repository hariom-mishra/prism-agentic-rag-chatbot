from pydantic_settings import BaseSettings
from pydantic import computed_field
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Setting(BaseSettings):
    DB_NAME: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    TOKEN_EXP: int = 86400
    ALGORITHM: str = "HS256"
    SECRET_KEY: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        encoded_password = quote_plus(self.DB_PASSWORD)
        # If password is empty, don't include the colon after user
        auth = f"{self.DB_USER}:{encoded_password}" if self.DB_PASSWORD else self.DB_USER
        return f"postgresql+asyncpg://{auth}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


setting = Setting()
