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
from queries.get_session_async_edgeql import get_session
from queries.insert_session_async_edgeql import insert_session
from queries.update_session_async_edgeql import update_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=configuration.telegram_bot_token)
dp = Dispatcher()


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
                base64_image = base64.b64encode(image_data).decode("utf-8")

                # Добавляем изображение в контент сообщения
                message_content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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
        # Get or create state based on existing conversation
        session_result = await get_session(
            gel_client.gel_client,
            chat_id=chat_id,
        )

        if session_result is None:
            logger.info("Новый пользователь - создаем новую сессию")
            # Новый пользователь - создаем новую сессию
            input_state = InputState(
                messages=[
                    HumanMessage(
                        content=message_content,
                    ),
                ],
            )
            # Используем встроенный метод .model_dump_json() для сериализации
            await insert_session(
                gel_client.gel_client,
                chat_id=chat_id,
                messages=input_state.model_dump_json(),
            )
        else:
            # Существующий пользователь - восстанавливаем сессию
            # Десериализуем сохраненные сообщения
            try:
                # Создаем state из сохраненных данных
                input_state = InputState.model_validate_json(session_result.messages)
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

        # Process the message through the graph
        result = await graph.ainvoke(input_state)

        logger.info(f"Result: {result}")

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
                state_obj = State(messages=result.messages)
                await update_session(
                    gel_client.gel_client,
                    chat_id=chat_id,
                    messages=state_obj.model_dump_json(),
                )
            elif isinstance(result, dict) and "messages" in result:
                # Создаем State из результата для правильной сериализации
                state_obj = State(messages=result["messages"])
                await update_session(
                    gel_client.gel_client,
                    chat_id=chat_id,
                    messages=state_obj.model_dump_json(),
                )
        elif hasattr(result, "messages") and result.messages:
            # Get the last AI message
            ai_message = result.messages[-1]
            response_text = ai_message.content

            # Update the session
            state_obj = State(messages=result.messages)
            await update_session(
                gel_client.gel_client,
                chat_id=chat_id,
                messages=state_obj.model_dump_json(),
            )
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
