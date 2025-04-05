from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from common.configuration import configuration


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text", "")
    txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
    return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.

    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(
        openai_api_key=configuration.ai_openai_api_key,
        model=model,
        model_provider=provider,
    )
