import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    DATABASE_URL: str = "postgresql://swimuser:swimpass@localhost:5432/swimdb"
    
    # API settings
    API_TITLE: str = "Swim Pipeline API"
    API_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
