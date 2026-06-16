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

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"mysql+asyncmy://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


setting = Setting()
