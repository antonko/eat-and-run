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

    if not user_text:
        await message.answer(
            "Пожалуйста, отправьте текстовое сообщение.",
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
            input_state = InputState(messages=[HumanMessage(content=user_text)])
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
                input_state.messages.append(HumanMessage(content=user_text))
            except Exception as e:
                logger.error(f"Ошибка при десериализации сообщений: {e}")
                # Если ошибка десериализации, создаем новую сессию
                input_state = InputState(messages=[HumanMessage(content=user_text)])

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
        except Exception as e:
            logger.error(f"Не удалось удалить сообщение о обработке: {e}")

        # Send the response
        await message.answer(response_text)

    except Exception as e:
        logger.exception(f"Error processing message: {e}")
        await message.answer(
            "Произошла ошибка при обработке сообщения. Пожалуйста, попробуйте еще раз.",
        )


async def start_bot() -> None:
    """Start the bot."""
    try:
        logger.info("Starting the bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    finally:
        logger.info("Bot stopped.")
        await bot.session.close()
