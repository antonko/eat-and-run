import base64
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message
from langchain_core.messages.human import HumanMessage

from agent.graph import graph
from agent.state import InputState, State
from common import gel_client
from common.configuration import configuration
from database.models.photos import PhotoModel
from database.models.users import UserModel
from database.repositories.photo_repository import PhotoRepository
from database.repositories.user_repository import UserRepository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=configuration.telegram_bot_token)
dp = Dispatcher()
user_repository = UserRepository(gel_client.gel_client)
photo_repository = PhotoRepository(gel_client.gel_client)


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle the /start command."""
    await message.answer(
        "Привет! Я бот-ассистент на базе ИИ. Задайте мне любой вопрос, и я постараюсь помочь.",
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle the /help command."""
    await message.answer(
        "Я могу ответить на различные вопросы и выполнить задачи, например:\n"
        "- Ответить на общие вопросы\n"
        "- Помочь с планированием питания\n"
        "- Сохранить информацию о приеме пищи\n"
        "- Показать статистику питания\n\n"
        "Просто напишите мне свой вопрос или запрос!",
    )


@dp.message()
async def handle_message(message: Message) -> None:
    """Handle all text messages."""
    user_text = message.text
    chat_id = str(message.chat.id)

    # Создаем массив для контента сообщения
    message_content = []

    # Добавляем текст, если он есть
    if user_text:
        message_content.append(
            {
                "type": "text",
                "text": user_text,
            },
        )
    # Если есть caption (подпись к медиа), используем его
    elif message.caption:
        message_content.append(
            {
                "type": "text",
                "text": message.caption,
            },
        )

    # Обрабатываем фотографии, если они есть
    if message.photo:
        # Берем только самое качественное изображение (последнее в массиве)
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)

        # Проверка на существование file_path
        if not file_info or not file_info.file_path:
            await message.answer(
                "Не удалось получить файл изображения. Пожалуйста, попробуйте еще раз.",
            )
        else:
            downloaded_file = await bot.download_file(file_info.file_path)

            # Проверка на существование скачанного файла
            if not downloaded_file:
                await message.answer(
                    "Не удалось скачать изображение. Пожалуйста, попробуйте еще раз.",
                )
            else:
                image_data = downloaded_file.read()
                image_data_base64 = base64.b64encode(image_data).decode("utf-8")

                # Получаем или создаем пользователя для привязки фотографии
                user = await user_repository.get_user_by_chat_id(chat_id)
                if not user:
                    # Новый пользователь - создаем запись
                    new_user = UserModel(chat_id=chat_id)
                    user = await user_repository.create_user(new_user)

                # Сохраняем фото в репозитории
                photo_model = PhotoModel(
                    file_data_base64=image_data_base64,
                    file_name=f"{photo.file_id}.jpg",
                    mime_type="image/jpeg",
                    user_id=str(user.id),
                )
                saved_photo = await photo_repository.save_photo(photo_model)

                # Добавляем информацию о изображении в контент сообщения
                message_content.append(
                    {
                        "type": "text",
                        "text": f"photo_id_int: {saved_photo.id_int}",
                    },
                )

    # Если нет ни текста, ни фото, запрашиваем у пользователя отправить сообщение
    if not message_content:
        await message.answer(
            "Пожалуйста, отправьте текстовое сообщение или фотографию.",
        )
        return

    # Send a processing message
    processing_msg = await message.answer("Обрабатываю ваш запрос...")

    try:
        # Получаем или создаем пользователя
        user = await user_repository.get_user_by_chat_id(chat_id)

        if not user:
            # Новый пользователь - создаем запись
            logger.info("Новый пользователь - создаем запись")
            new_user = UserModel(chat_id=chat_id)
            user = await user_repository.create_user(new_user)

            # Создаем новую сессию для нового пользователя
            input_state = InputState(
                messages=[
                    HumanMessage(
                        content=message_content,
                    ),
                ],
                user_id=user.id,
            )
            # Создаем и сохраняем новую сессию
            user.state = input_state.model_dump_json()
            await user_repository.update_user(user)
        else:
            # Существующий пользователь - обновляем статистику
            user.interaction_count += 1
            user = await user_repository.update_user(user)

            # Десериализуем сохраненные сообщения
            try:
                # Проверяем, является ли state строкой или словарем
                if isinstance(user.state, dict):
                    input_state = InputState.model_validate(user.state)
                else:
                    input_state = InputState.model_validate_json(user.state)

                # Добавляем новое сообщение пользователя
                input_state.messages.append(
                    HumanMessage(
                        content=message_content,
                    ),
                )
            except Exception:
                logger.exception("Ошибка при десериализации сообщений")
                # Если ошибка десериализации, создаем новую сессию
                input_state = InputState(messages=[HumanMessage(content=message_content)])
                user.state = input_state.model_dump_json()

        # Process the message through the graph
        result = await graph.ainvoke(
            input_state,
        )

        # Get the AI response from the result
        response_text = (
            "Извините, не удалось обработать ваш запрос. Пожалуйста, попробуйте еще раз."
        )

        if isinstance(result, dict) and "messages" in result and result["messages"]:
            # Get the last AI message
            ai_message = result["messages"][-1]
            response_text = ai_message.content

            # Update the session with all messages
            if hasattr(result, "messages"):
                # Создаем State из результата для правильной сериализации
                state_obj = State(messages=result.messages, user_id=user.id)
                user.state = state_obj.model_dump_json()
                await user_repository.update_user(user)
            elif isinstance(result, dict) and "messages" in result:
                # Создаем State из результата для правильной сериализации
                state_obj = State(messages=result["messages"], user_id=user.id)
                user.state = state_obj.model_dump_json()
                await user_repository.update_user(user)
        elif hasattr(result, "messages") and result.messages:
            # Get the last AI message
            ai_message = result.messages[-1]
            response_text = ai_message.content

            # Update the session
            state_obj = State(messages=result.messages, user_id=user.id)
            user.state = state_obj.model_dump_json()
            await user_repository.update_user(user)
        elif hasattr(result, "output"):
            response_text = result.output
        elif isinstance(result, dict) and "output" in result:
            response_text = result["output"]

        # Delete the processing message
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
            )
        except Exception:
            logger.exception("Не удалось удалить сообщение о обработке")

        # Send the response
        await message.answer(response_text)

    except Exception:
        logger.exception("Error processing message")
        await message.answer(
            "Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте еще раз.",
        )


async def start_bot() -> None:
    """Start the bot."""
    try:
        logger.info("Starting the bot...")
        await dp.start_polling(bot)
    except Exception:
        logger.exception("Failed to start bot")
    finally:
        logger.info("Bot stopped.")
        await bot.session.close()
