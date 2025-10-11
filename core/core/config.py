from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str  # اصلاح املای ALCHAMY → ALCHEMY

    model_config = SettingsConfigDict(env_file=".env")  # اصلاح mosel_config → model_config

settings = Settings()
