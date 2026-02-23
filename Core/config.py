from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASEURL: str
    ASYNC_DATABASEURL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RESET_TOKEN_EXPIRE_MINUTES: int = 15
    EMAIL_ADDRESS: EmailStr
    EMAIL_PASSWORD: str
    SMTP_SERVER: str
    SMTP_PORT: int

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()