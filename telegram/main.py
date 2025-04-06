import asyncio
import logging

from common.configuration import configuration
from telegram.bot import start_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Главная функция приложения."""
    try:
        if not configuration.telegram_bot_token:
            logger.error("TELEGRAM_BOT_TOKEN is not set in the environment variables.")
            return

        logger.info("Starting bot...")
        await start_bot()

    except Exception:  # noqa: BLE001
        logger.exception("Application error")


if __name__ == "__main__":
    asyncio.run(main())
