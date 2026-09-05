from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str
    ALGORITHM: str = "HS256"
    ACCES_TOKEN_EXPIRE: int = 60 
    REFRESH_TOKEN_TIME: int = 7 * 24 * 60
    SECRET_KEY: str 
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "src" / ".env", 
        extra="ignore",
        env_file_encoding="utf-8"
        
    )
    
settings = Settings()