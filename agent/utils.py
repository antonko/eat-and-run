from langchain_openai import ChatOpenAI

from common.configuration import configuration


def load_chat_model() -> ChatOpenAI:
    """Загружает модель для чата."""
    return ChatOpenAI(
        model=configuration.ai_default_model,
        api_key=configuration.ai_openai_api_key,
        max_tokens=1000,
        temperature=0,
    )
