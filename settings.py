from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings that can be loaded from environment variables."""
    
    # Database configuration
    gel_host: str = "localhost"
    gel_port: int = 5656
    gel_user: Optional[str] = "test"
    gel_password: Optional[str] = "test"
    gel_branch: Optional[str] = "main"
    gel_tls_security: Optional[str] = "strict"
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Create settings instance
settings = Settings() 