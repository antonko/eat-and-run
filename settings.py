from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings that can be loaded from environment variables."""

    # Database configuration
    gel_host: str = "localhost"
    gel_port: int = 5656
    gel_user: str = "test"
    gel_password: str = "test"  # noqa: S105
    gel_branch: str = "main"
    gel_tls_security: str = "strict"
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Create settings instance
settings = Settings()
