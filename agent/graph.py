import datetime
from typing import Literal, cast

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from agent.state import InputState, State
from agent.tools import TOOLS
from agent.utils import load_chat_model


async def call_model(
    state: State,
    config: RunnableConfig,
) -> dict[str, list[AIMessage]]:
    """Вызывает модель для получения ответа."""
    llm = load_chat_model()
    model = llm.bind_tools(TOOLS)

    system_message = """
    Вы — интеллектуальный помощник по питанию и спорту. Ваша задача — помогать пользователям отслеживать свой рацион и физическое состояние, в том числе анализируя фотографии еды.

    Когда вы получаете изображение, выполните следующие шаги:
    4. **Если изображение содержит реальную, безопасную и реалистичную порцию еды:**
       - Определите блюдо (укажите название на русском языке)
       - Оцените примерный вес в граммах
       - Оцените калорийность
       - Определите количество белков, жиров и углеводов (в граммах)

    Всю полученную информацию, включая изображение, следует сохранять в базу данных пользователя **только в том случае, если пользователь не указал иное**.
    """

    system_message += (
        f"\nТекущее время: {datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')}"
    )

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
