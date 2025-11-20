import os
import json
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "signalscope"
    SECRET_KEY: str = "your-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # CORS origins - supports JSON array format or comma-separated values
    cors_origins: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Explicitly read CORS_ORIGINS from environment if not set by Pydantic
        env_cors = os.getenv("CORS_ORIGINS")
        if env_cors:
            self.cors_origins = env_cors
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS - supports both JSON array and comma-separated values"""
        cors_value = os.getenv("CORS_ORIGINS", self.cors_origins).strip()
        
        if not cors_value:
            return []
        
        # Remove outer quotes if present
        if cors_value.startswith('"') and cors_value.endswith('"'):
            cors_value = cors_value[1:-1].replace('\\"', '"')
        
        # Try parsing as JSON array first
        try:
            parsed = json.loads(cors_value)
            return parsed if isinstance(parsed, list) else [str(parsed)]
        except json.JSONDecodeError:
            # Not JSON, try comma-separated values
            if ',' in cors_value:
                return [origin.strip().strip('"').strip("'") for origin in cors_value.split(',')]
            return [cors_value]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

