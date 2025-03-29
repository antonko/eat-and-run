import asyncio
import logging

from app.bot import start_bot
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Main application entry point."""
    try:
        # Verify required configuration
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN is not set in the environment variables.")
            return

        if not settings.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is not set in the environment variables.")
            return

        # Start the bot
        logger.info("Starting the food analysis bot...")
        await start_bot()

    except Exception as e:
        logger.error(f"Application error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
