import logging
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.info("Loaded environment variables from .env file")


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # OpenAI API Key
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # OpenAI model to use - изменено для поддержки vision
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def check_config(self) -> bool:
        """Проверка наличия всех необходимых настроек."""
        if not self.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables")
            return False

        if not self.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not set in environment variables")
            return False

        logger.info(f"Using OpenAI model: {self.OPENAI_MODEL}")
        return True


# Initialize settings
settings = Settings()
if not settings.check_config():
    logger.warning(
        "Some required settings are missing. Bot may not function correctly."
    )
