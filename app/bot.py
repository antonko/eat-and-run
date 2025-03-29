import logging

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message

from app.config import settings
from app.food_analyzer import FoodAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
# session = AiohttpSession()
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Initialize food analyzer
food_analyzer = FoodAnalyzer()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle the /start command."""
    await message.answer(
        "Привет! Я бот для анализа еды. Отправь мне фотографию блюда, "
        "и я определю, что это за блюдо, его примерный вес и пищевую ценность (КБЖУ)."
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle the /help command."""
    await message.answer(
        "Я могу анализировать фотографии еды и определять:\n"
        "- Название блюда\n"
        "- Примерный вес\n"
        "- Калорийность\n"
        "- Содержание белков, жиров и углеводов\n\n"
        "Просто отправь мне фотографию блюда!"
    )


@dp.message(lambda message: message.photo)
async def handle_photo(message: Message):
    """Handle incoming photos."""
    # Проверяем, что фотографии действительно есть
    if not message.photo:
        await message.answer(
            "Не удалось получить фотографию. Пожалуйста, попробуйте еще раз."
        )
        return

    # Get the largest photo (best quality)
    photo = message.photo[-1]

    try:
        # Send a processing message
        processing_msg = await message.answer("Анализирую фотографию...")

        # Download the photo
        file_info = await bot.get_file(photo.file_id)

        # Проверка на существование file_path
        if not file_info or not file_info.file_path:
            await message.answer(
                "Не удалось получить файл изображения. Пожалуйста, попробуйте еще раз."
            )
            return

        downloaded_file = await bot.download_file(file_info.file_path)

        # Проверка на существование скачанного файла
        if not downloaded_file:
            await message.answer(
                "Не удалось скачать изображение. Пожалуйста, попробуйте еще раз."
            )
            return

        image_data = downloaded_file.read()

        # Analyze the image
        analysis_result = await food_analyzer.analyze_image(image_data)

        # Format and send the response
        if analysis_result.get("is_food", False):
            response_text = (
                f"✅ Блюдо: {analysis_result['name']}\n"
                f"⚖️ Примерный вес: {analysis_result['weight_g']} г\n"
                f"🔥 Калорийность: {analysis_result['calories']} ккал\n\n"
                f"📊 Пищевая ценность:\n"
                f"🥩 Белки: {analysis_result['macros']['protein_g']} г\n"
                f"🧈 Жиры: {analysis_result['macros']['fat_g']} г\n"
                f"🍚 Углеводы: {analysis_result['macros']['carbs_g']} г"
            )
        else:
            response_text = "⚠️ " + analysis_result.get(
                "message", "Не удалось распознать еду на изображении."
            )

        # Delete the processing message and send the result
        try:
            await bot.delete_message(
                chat_id=message.chat.id, message_id=processing_msg.message_id
            )
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение о обработке: {e}")

        await message.answer(response_text)

    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await message.answer(
            "Произошла ошибка при обработке фотографии. Пожалуйста, попробуйте еще раз."
        )


@dp.message()
async def handle_message(message: Message):
    """Handle all other messages."""
    await message.answer(
        "Отправь мне фотографию еды для анализа. "
        "Также можешь использовать команду /help для получения справки."
    )


async def start_bot():
    """Start the bot."""
    try:
        logger.info("Starting the bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    finally:
        logger.info("Bot stopped.")
        await bot.session.close()
