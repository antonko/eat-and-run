import logging
from http.client import HTTPConnection
from typing import Literal, cast

from langchain.globals import set_debug
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from agent.state import InputState, State
from agent.tools import TOOLS
from agent.utils import load_chat_model
from common.configuration import configuration

# Включение детального логирования для httpx и openai
set_debug(True)
logging.basicConfig(level=logging.DEBUG)
HTTPConnection.debuglevel = 1

loggers = [
    logging.getLogger("httpx"),
    logging.getLogger("openai"),
    logging.getLogger("httpcore"),
]

for logger in loggers:
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


async def call_model(
    state: State,
    config: RunnableConfig,
) -> dict[str, list[AIMessage]]:
    """Вызывает модель для получения ответа."""
    model = load_chat_model(configuration.ai_default_model).bind_tools(TOOLS)

    system_message = "You are a helpful assistant."

    response = cast(
        "AIMessage",
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages],
            config,
        ),
    )

    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question "
                    "in the specified number of steps.",
                ),
            ],
        }

    return {"messages": [response]}


builder = StateGraph(State, input=InputState)

builder.add_node(call_model)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_edge("__start__", "call_model")


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Определяет следующий шаг в зависимости от ответа модели."""
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise TypeError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}",
        )
    # If there is no tool call, then we finish
    if not last_message.tool_calls:
        return "__end__"
    # Otherwise we execute the requested actions
    return "tools"


builder.add_conditional_edges(
    "call_model",
    route_model_output,
)

builder.add_edge("tools", "call_model")

graph = builder.compile(
    interrupt_before=[],
    interrupt_after=[],
)
graph.name = "Eat and Run"
